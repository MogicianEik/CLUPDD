#!/usr/local/Python-3.7/bin/python

import cgi
import cgitb
import pymysql

cgitb.enable()

# retrieve form data, if any
form = cgi.FieldStorage()

print("Content-type: text/html\n")

if form:
    connection = pymysql.connect(db='group_C',user='test',password='test',port = 4253)
    cursor = connection.cursor()
    
    #snp query
    if "chromosome" in form:
        chrom = form.getvalue("chromosome")
        pos = form.getvalue("position")
        query = """
        SELECT reference.allele, snpeffect.allele, effect, impact, gene.name, description, count(*)
        FROM reference JOIN snp USING(RPID) 
        JOIN snpeffect USING(SNPID)
        JOIN associate USING(RPID)
        JOIN gene USING(GID)
        JOIN infunction USING(GID)
        JOIN goterm USING(GOID)
        WHERE reference.chromosome = '%s' AND position = %s GROUP BY description""" % (chrom, pos)
        
        #test query
        
        cursor.execute(query)
        rows=cursor.fetchall()
        print("<table id=snp_search>")
        print("<tr><th>Ref Allele</th><th>SNP</th><th>Effect</th><th>Impact</th><th>Gene name</th><th>Description</th></tr>")
        for row in rows:
            print("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2],row[3],row[4],row[5]))
        print("</table>")
    
    connection.close()

