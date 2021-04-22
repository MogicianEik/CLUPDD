#!/usr/local/Python-3.7/bin/python

import cgi
import cgitb
import pymysql

cgitb.enable()

# retrieve form data, if any
form = cgi.FieldStorage()

print("Content-type: text/html\n")

if form:
    connection = pymysql.connect(host='bioed.bu.edu',db='group_C',user='test',password='test')
    cursor = connection.cursor()
    
    search_snp = form.getvalue("search_snp")
    if search_snp:
        #snp query
        chrom = form.getvalue("chromosome")
        pos = form.getvalue("position")
        #query = """
        #SELECT reference.allele, snpeffect.allele, effect, impact, gene.name, description
        #FROM reference JOIN snp USING(RPID) 
        #JOIN snpeffect USING(SNPID)
        #JOIN associate USING(RPID)
        #JOIN gene USING(GID)
        #JOIN infunction USING(GID)
        #JOIN goterm USING(GOID)
        #WHERE reference.chromosome = '%s' AND position = %s""" % (chrom, pos)
        
        #test query
        chrom = form.getvalue("chromosome")
        pos = form.getvalue("position")
        query= '''
        SELECT goid, name, description
        FROM goterm
        WHERE description LIKE "%s" ''' %pos
        
        cursor.execute(query)
        rows=cursor.fetchall()
    
        for row in rows:
            print("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2]))
    
    if search_gene:
        #gene query
        
        cursor.execute(query)
        rows=cursor.fetchall()
    
        for row in rows:
            print("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2]))
    
    if search-region:
        #region query
        
        cursor.execute(query)
        rows=cursor.fetchall()
    
        for row in rows:
            print("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2]))
    
    if advanced_search:
        #advanced query
        
        cursor.execute(query)
        rows=cursor.fetchall()
    
        for row in rows:
            print("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2]))
    
    