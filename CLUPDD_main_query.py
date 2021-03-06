#!/usr/local/Python-3.7/bin/python

####################################
############ CLUPDD CGI ############
####################################

#################
#### Imports ####
#################

import cgi
import cgitb
import pymysql
import pandas as pd

###################
#### Functions ####
###################


def allele_freq(position,full_df):
    snp_df = full_df.loc[full_df['Position'] == position]
    pops = pd.unique(snp_df['name'])
    return_dic = {}
    for pop in pops:
        column_name = pop+'_AltFreq'
        return_dic[column_name] = ''
        allele_counts = snp_df.loc[snp_df['name']== pop]['GT'].str.split('/').explode().value_counts()
        if allele_counts.sort_index().index.all() == '0':
            return_dic[column_name] = '0'
        else:
            for allele in allele_counts.index:
                if allele != "0":
                    return_dic[column_name] = return_dic[column_name] + str("{0:.3f}".format(allele_counts.loc[allele]/allele_counts.sum())) + ' '
    return(pd.Series(return_dic))

def allele_freq_small(snp_df):
    pops = pd.unique(snp_df['name'])
    return_dic = {}
    for pop in pops:
        column_name = pop+'_AltFreq'
        return_dic[column_name] = ''
        allele_counts = snp_df.loc[snp_df['name']== pop]['GT'].str.split('/').explode().value_counts()
        if allele_counts.sort_index().index.all() == '0':
            return_dic[column_name] = '0'
        else:
            for allele in allele_counts.index:
                if allele != "0":
                    return_dic[column_name] = return_dic[column_name] + str("{0:.3f}".format(allele_counts.loc[allele]/allele_counts.sum())) + ' '
    return(pd.Series(return_dic))

def print_head(df): 
    #for printing the column names of a dataframe
    table_head = "<tr>"
    for name in df.columns:
        table_head = table_head + "<th>%s</th>" % name
    table_head = table_head + "</tr>"
    print(table_head)
    
def print_data(df):
    #for printing the data in a dataframe
    for index, row in df.iterrows():
        table_row = "<tr>"
        for value in row:
            value = str(value)
            table_row = table_row + "<td>%s</td>" % value
        table_row = table_row + "</tr>"
        print(table_row)
        
def print_go_terms(df):
    #for printing out the GO terms from a dataframe
    for index, row in df.iterrows():
        table_row = "<tr>"
        for value in row:
            value = str(value)
            if value in ['molecular_function','cellular_component','biological_process']:
                table_row = table_row + '<td style="font-weight: bold;">- %s -</td>' % value
            else:
                table_row = table_row + "<td>%s</td>" % value
        table_row = table_row + "</tr>"
        print(table_row)    
        

####################
#### Prep Steps ####
####################

cgitb.enable()
form = cgi.FieldStorage()
connection = pymysql.connect(db='group_C',user='test',password='test', port = 4253) 

if form:
    print("Content-type: text/html\n")
    submit = form.getvalue('submit')
    
    ####################
    #### Gene Query ####
    ####################

    if submit == "submitgene":
        # get values
        gene = form.getvalue('gene')
        radio = form.getvalue('radio')

        # define queries
        if radio == "symbol":
            query1 = '''
            select gene.name as Name, reference.chromosome as Chrom, reference.position as Position, reference.allele Ref_Allele, group_concat(distinct snpeffect.allele) Alt_Allele, group_concat(distinct effect) as Effect, Impact, GT, population.name
            from gene join associate using(gid) 
            join reference using(rpid) 
            join snp using(rpid) 
            join snpeffect using(snpid)
            join have using(snpid)
            join sample using(sid) 
            join population using(pid)
            where gene.symbol regexp '%s?' or gene.symbol = '%s'
            group by rpid, sid
            ''' % (gene, gene)

            query2='''
            select goterm.name as GO_term, Description, gene.name as Gene
            from gene left join infunction using(GID)
            left join goterm using(GOID)
            where gene.symbol regexp '%s?' or gene.symbol = '%s'
            ''' % (gene, gene)

        if radio == "name":
            query1 = '''
            select gene.name as Name, reference.chromosome as Chrom, reference.position as Position, reference.allele Ref_Allele, group_concat(distinct snpeffect.allele) Alt_Allele, group_concat(distinct effect) as Effect, Impact, GT, population.name
            from gene join associate using(gid) 
            join reference using(rpid) 
            join snp using(rpid) 
            join snpeffect using(snpid)
            join have using(snpid)
            join sample using(sid) 
            join population using(pid)
            where gene.name regexp '%s?' or gene.name = '%s'
            group by rpid, sid
            ''' % (gene, gene)

            query2='''
            select goterm.name as GO_term, Description, gene.name as Gene
            from gene left join infunction using(GID)
            left join goterm using(GOID)
            where gene.name regexp '%s?' or gene.name = '%s'
            ''' % (gene, gene)
        
        # Excecute queries
        temp_df = pd.read_sql(query1,connection)
        go_terms = pd.read_sql(query2,connection)
        
        # Alter data
        temp_df_small = temp_df.drop(['GT', 'name'], axis = 1).drop_duplicates(ignore_index=True)
        gene_results = temp_df_small.join(temp_df_small['Position'].apply(lambda x: allele_freq(x,temp_df)), how='left', lsuffix='_left', rsuffix='_right')

        #print SNPs
        print("<h3>SNPs In %s</h3>" % gene)
        print("<div style='overflow-x: scroll;'>")
        print("<table id=gene_search>")
        print_head(gene_results)
        print_data(gene_results)
        print("</table>")
        print('</div>')
        print("<br></br>")

        #Print features
        print("<h3>GO Terms For %s</h3>" % gene)
        print("<div style='overflow-x: scroll;'>")
        print("<table>")
        print_head(go_terms)
        print_go_terms(go_terms)
        print("</table>")
        print('</div>')


    ###################
    #### SNP Query ####
    ###################

    if submit == "submitsnp":
        # Get values
        chrom = form.getvalue("chromosome")
        pos = form.getvalue("position")

        # Define queries
        query1 = """
        SELECT reference.allele as Ref_allele, snpeffect.allele as Alt_allele, Effect, Impact,gene.Feature_type, gene.Name, gene.Symbol, Description
        FROM reference JOIN snp USING(RPID) 
        JOIN snpeffect USING(SNPID)
        JOIN associate USING(RPID)
        JOIN gene USING(GID)
        JOIN infunction USING(GID)
        JOIN goterm USING(GOID)
        WHERE reference.chromosome = '%s' AND position = %s
        GROUP BY description""" % (chrom, pos)

        query2 = '''
        SELECT GT, population.name 
        FROM reference JOIN snp USING(RPID)
        JOIN have USING (snpid)
        JOIN sample USING (sid)
        JOIN population using (pid)
        Where reference.chromosome = '%s' AND position = %s''' % (chrom, pos)
        
        # Execute queries
        gene_temp_df = pd.read_sql(query1,connection)
        pop_temp_df = pd.read_sql(query2,connection)

        #printing snp info
        snpInfo = gene_temp_df.drop(['Description','Name'], axis=1).drop_duplicates(ignore_index=True)
        print('<h3>SNP Information for SNP at %s, Position %s</h3>' % (chrom, pos)) 
        print("<div style='overflow-x: scroll;'>")
        print('<table>')
        print_head(snpInfo)
        print_data(snpInfo)
        print('</table>')
        print('</div>')
        print('<br></br>')

        #printing effected gene
        genes = gene_temp_df[['Feature_type','Name','Symbol']].drop_duplicates()
        print('<h3>Gene Effected By SNP</h3>')
        print("<div style='overflow-x: scroll;'>")
        print('<table>')
        print_head(genes)
        for index, row in genes.iterrows():
            table_row = "<tr>"
            if row[0] == 'gene':
                for i, value in enumerate(row):
                    if i == 2:
                        table_row = table_row + "<td><a href='https://www.ncbi.nlm.nih.gov/search/all/?term=%s&ac=no&sp=r'>%s</a></td>" % (value, value)
                    else:
                        table_row = table_row + "<td>%s</td>" % value
            else:
                for value in row:
                    value = str(value)
                    table_row = table_row + "<td>%s</td>" % value
            table_row = table_row + "</tr>"
            print(table_row)
        print('</table>')
        print('</div>')
        print('<br></br>')

        #printing GO terms
        go = gene_temp_df['Description']
        print('<h3>Associated GO Terms</h3>')
        print("<div style='overflow-x: scroll;'>")
        print('<table>')
        print('<tr><th>GO Terms</th><tr>')
        for index, item in go.iteritems():
            item = str(item)
            if item in ['molecular_function','cellular_component','biological_process']:
                print('<tr><td style="font-weight: bold;">- %s -</td></tr>' % item)
            else:
                print('<tr><td>%s</td></tr>' % item)
        print('</table>')
        print('</div>')
        print('<br></br>')

        #printing pop info
        af = allele_freq_small(pop_temp_df)
        print("<h3>Alternate Allele Frequencies For Populations With SNP</h3>")
        print("<div style='overflow-x: scroll;'>")
        print('<table>')
        print('<tr><th>Population</th><th>Allele Frequency</th></tr>')
        for index, item in af.iteritems():
            print('<tr><td>%s</td><td>%s</td></tr>' % (index, item)) 
        print('</table>')
        print('</div>')


    ######################
    #### Region Query ####
    ######################

    if submit == "submitregion":
        # Get values
        chrom = form.getvalue("chromosome")
        strt = form.getvalue("start")
        end = form.getvalue("end")

        # Define queries
        query1 = """
        SELECT reference.chromosome as Chromosome, reference.position as Position, reference.allele AS Ref_allele, alt_allele AS Alt_allele
        FROM reference JOIN snp USING(RPID)
        WHERE chromosome = '%s' AND position BETWEEN %s AND %s
        """ % (chrom, strt, end)

        query2 = """
        SELECT Chromosome, Start_position, End_position, feature_type, name, symbol
        FROM gene
        WHERE chromosome = '%s' AND start_position BETWEEN %s AND %s 
        OR end_position BETWEEN %s AND %s 
        OR start_position < %s AND end_position > %s
        """ % (chrom, strt, end, strt, end, strt, end)

        # Execute queries
        snplist_temp_df = pd.read_sql(query1,connection)
        genelist_temp_df = pd.read_sql(query2,connection)
        
        # Print SNPs
        print('<h3>SNPs Found in %s Position %s-%s</h3>' %(chrom,strt,end))
        print("<div style='overflow-x: scroll;'>")
        print('<table>')
        print_head(snplist_temp_df)
        print_data(snplist_temp_df)
        print('</table>')
        print('</div>')
        print('<br></br>')
        
        # Print Genes
        print('<h3>Genomic Features Found in %s Position %s-%s</h3>' %(chrom,strt,end))
        print("<div style='overflow-x: scroll;'>")
        print('<table>')
        print_head(genelist_temp_df)
        for index, row in genelist_temp_df.iterrows():
            table_row = "<tr>"
            if row[3] == 'gene':
                for i, value in enumerate(row):
                    if i == 5:
                        table_row = table_row + "<td><a href='https://www.ncbi.nlm.nih.gov/search/all/?term=%s&ac=no&sp=r'>%s</a></td>" % (value, value)
                    else:
                        table_row = table_row + "<td>%s</td>" % value
            else:
                for value in row:
                    value = str(value)
                    table_row = table_row + "<td>%s</td>" % value
            table_row = table_row + "</tr>"
            print(table_row)
        print('</table>')
        print('</div>')


    ########################
    #### Advanced Query ####
    ########################

    if submit == "submitadvanced":
        # Get value
        query = form.getvalue("query")
        
        # Execute Query
        temp_df = pd.read_sql(query,connection)

        # Print results
        print('<h3>Results for Advanced Query</h3>')
        print("<div style='overflow-x: scroll;'>")
        print('<table>')
        print_head(temp_df)
        print_data(temp_df)
        print('</table>')
        print('</div>')
    

##############################
#### Close out connection ####
##############################

connection.close()
        
        

