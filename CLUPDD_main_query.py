#!/usr/local/Python-3.7/bin/python

import cgi
import cgitb
import pymysql
import pandas as pd

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



cgitb.enable()

# retrieve form data, if any
form = cgi.FieldStorage()

print("Content-type: text/html\n")

if form:
    submit = form.getvalue("submit")
    
     #snp query
    if submit == "submitsnp":
        connection = pymysql.connect(db='group_C',user='test',password='test',port = 4253)

        chrom = form.getvalue("chromosome")
        pos = form.getvalue("position")

        query1 = """
        SELECT reference.allele as Ref_allele, snpeffect.allele as Alt_allele, Effect, Impact, gene.Name, Description
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

        gene_temp_df = pd.read_sql(query1,connection)
        pop_temp_df = pd.read_sql(query2,connection)

        #printing snp info
        snpInfo = gene_temp_df.drop(['Description','Name'], axis=1).drop_duplicates(ignore_index=True)

        print('<table>')
        head = '<tr>'
        for name in snpInfo.columns:
            head = head + '<th>%s</th>' %name
        head = head + '</tr>'
        print(head)

        for index, row in snpInfo.iterrows():
            data = '<tr>'
            for item in row:
                data = data + '<td>%s</td>' % item
            data = data + '</tr>'
            print(data)

        #printing effected gene
        genes = gene_temp_df['Name'].drop_duplicates()
        print('<table>')
        print('<tr><th>Genes Affected by SNP</th></tr>')
        for index, item in genes.iteritems():
            print('<tr><td>%s</td></tr>' % item)
        print('</table>')

        #printing GO terms
        go = gene_temp_df['Description']
        print('<table>')
        print('<tr><th>Associated GO Terms</th><tr>')
        for idex, item in go.iteritems():
            print('<tr><td>%s</td></tr>' % item)
        print('</table>')

        #printing pop info
        af = allele_freq_small(pop_temp_df)
        print('<table>')
        print('<tr><th>Population</th><th>Alternate Allele Frequency</th></tr>')
        for index, item in af.iteritems():
            print('<tr><td>%s</td><td>%s</td></tr>' % (index, item)) 
        print('</table>')   

        connection.close()

    if submit == "submitgene":
        connection = pymysql.connect(db='group_C',user='test',password='test',port = 4253)
        
        gene = form.getvalue('gene')
        radio = form.getvalue('radio')
        
        if radio == 'symbol':
            query = '''
            select reference.position as Position, reference.allele Ref_Allele, group_concat(distinct snpeffect.allele) Alt_Allele, group_concat(distinct effect) as Effect, Impact, GT, population.name
            from gene join associate using(gid) 
            join reference using(rpid) 
            join snp using(rpid) 
            join snpeffect using(snpid)
            join have using(snpid)
            join sample using(sid) 
            join population using(pid)
            where gene.symbol = '%s' 
            group by rpid, sid
            ''' % gene
        
        if radio == 'name':
            query = '''
            select reference.position as Position, reference.allele Ref_Allele, group_concat(distinct snpeffect.allele) Alt_Allele, group_concat(distinct effect) as Effect, Impact, GT, population.name
            from gene join associate using(gid) 
            join reference using(rpid) 
            join snp using(rpid) 
            join snpeffect using(snpid)
            join have using(snpid)
            join sample using(sid) 
            join population using(pid)
            where gene.name = '%s' 
            group by rpid, sid
            ''' % gene

        temp_df = pd.read_sql(query,connection)
        temp_df_small = temp_df.drop(['GT','name'], axis = 1).drop_duplicates(ignore_index=True)
        gene_results = temp_df_small.join(temp_df_small['Position'].apply(lambda x: allele_freq(x,temp_df)))

        print("<table id=gene_search>")

        table_head = "<tr>"
        for name in gene_results.columns:
            table_head = table_head + "<th>%s</th>" % name
        table_head = table_head + "</tr>"
        print(table_head)

        for index, row in gene_results.iterrows():
            table_row = "<tr>"
            for value in row:
                value = str(value)
                table_row = table_row + "<td>%s</td>" % value
            table_row = table_row + "</tr>"
            print(table_row)

        print("</table>")
        
        connection.close()
