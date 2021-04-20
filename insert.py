import pandas as pd
import vcf
import pymysql

# a vcf parser to pandas pd
def read_vcf(vcf_file):
    vcf_reader = vcf.Reader(open(vcf_file))
    res=[]
    cols = ['sample','REF','ALT','GT','GQ','chrom','POS','FILTER',
             'var_type','sub_type','start','end','QUAL','INFO']

    for rec in vcf_reader:
        x = [rec.CHROM, rec.POS, rec.FILTER, rec.var_type, rec.var_subtype, rec.start, rec.end, rec.QUAL, rec.INFO]
        for sample in rec.samples:
            if sample.gt_bases == None:
                #no call
                mut=''
                row = [sample.sample, rec.REF, sample.gt_bases, 0,0]
            elif rec.REF != sample.gt_bases:
                mut = str(rec.end)+rec.REF+'>'+sample.gt_bases
                cdata = sample.data
                row = [sample.sample, rec.REF, sample.gt_bases, cdata[0], cdata[3]
                      ] + x
            else:
                #call is REF
                mut = str(rec.end)+rec.REF              
                cdata = sample.data
                row = [sample.sample, rec.REF, sample.gt_bases, cdata[0], cdata[3]
                      ] + x

            res.append(row)
    res = pd.DataFrame(res,columns=cols)
    res = res[~res.start.isnull()]
    return res
    
# get all samples in this insert
def get_samples(df):
    return sorted(list(set(list(df['sample']))))

# TODO: on html cgi, check repeat insertion with the exsisiting data base, dump the repeat ones    
def insert_goterm(go_file):
    infile = open(go_file,'r')
    connection = pymysql.connect(db='group_C', user='test',
                       passwd='test',
                       port = 4253)
    cursor = connection.cursor()
    for line in infile.readlines():
        term = line[:10]
        des = line[11:-1] # get rid of newlines in the goterm file
        query = '''INSERT INTO goterm(name,description) VALUES ("{}","{}")'''.format(term,des) # tolerate ' in descriptions
        cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    infile.close()

    
# a huge insert, update all tables except goterm, gene at one time
def insert(df, enotes, pdic):
    # order of insert, experiment(one time), population(in a loop), sample(in a loop), reference(in a loop), snp (huge loop), snpeffect, have
    connection = pymysql.connect(db='group_C', user='test',
                       passwd='test',
                       port = 4253)
    cursor = connection.cursor()
    
    # insert into experiment TODO: make notes mandatory on the html page
    query = '''INSERT INTO experiment(notes) VALUES ("{}")'''.format(notes)
    cursor.execute(query)
    connection.commit()
    
    # insert into population TODO: pdic come from user input on the html page. pdic is a dictionary where keys are sample identifiers and values are which polutions they belong to and sample notes.
    pnames = list(set([pdic[x][0] for x in pdic])) # remove repeats, pdic[x][1] is the note for that sample
    for pname in pnames:
        query = '''INSERT INTO population(name) VALUES ("{}")'''.format(pname)
        cursor.execute(query)
    cursor.commit()
    
    # insert into sample
    query = '''SELECT EID FROM experiment WHERE notes = "{}";'''.format(enotes)
    cursor.execute(query)
    results = cursor.fetchall()
    EID = results[0]
    for sname in pdic:
        query = '''SELECT PID FROM population WHERE name = "{}";'''.format(pdic[sname][0])
        cursor.execute(query)
        results = cursor.fetchall()
        PID = results[0]
        query = '''INSERT INTO sample(PID, EID, identifier, notes) VALUES ({},{},'{}','{}')'''.format(PID,EID,sname,pdic[sname][1])
        cursor.execute(query)
    connection.commit()
    
    # insert into reference
    temp = df[['REF','chrom','POS']] #subset a tmp df to extract ref info
    temp.drop_duplicates(inplace=True)
    for index, row in temp.iterrows():
        query = '''INSERT INTO reference(chromosome, position, allele) VALUES ("{}",{},"{}")'''.format(row['chrom'],int(row['POS']),row['REF'])
        cursor.execute(query)
    connection.commit()
    
    # insert into SNP, have, and snpeffect
    snpeff = []
    for index, row in df.iterrows():
        # get the corresponding RPID 
        query = '''SELECT RPID FROM reference WHERE chromosome = "{}" AND position = {} AND allele = "{}"'''.format(row['chrom'],int(row['POS']),row['REF'])
        cursor.execute(query)
        results = cursor.fetchall()
        RPID = results[0]
        # get all info for SNP
        query = '''INSERT INTO snp(PRID,alt_allele,qual,filter,AC,AF,AN,baseQRankSum,clippingRankSum,DP,excessHet,FS,inbreedingCoeff,MLEAC,MLEAF,MQ,MQRankSum,QD,readPosRankSUM,SOR)
                    VALUES({},"{}",{},"{}",{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})'''.format(PRID,
                    row['ALT'],
                    float(row['QUAL']),
                    row['FILTER'],
                    row['INFO']['AC'][0],
                    row['INFO']['AF'][0],
                    row['INFO']['AN'],
                    row['INFO']['BaseQRankSum'],
                    row['INFO']['ClippingRankSum'],
                    row['INFO']['DP'],
                    row['INFO']['ExcessHet'],
                    row['INFO']['FS'],
                    row['INFO']['InbreedingCoeff'],
                    row['INFO']['MLEAC'][0],
                    row['INFO']['MLEAF'][0],
                    row['INFO']['MQ'],
                    row['INFO']['MQRankSum'],
                    row['INFO']['QD'],
                    row['INFO']['ReadPosRankSum'],
                    row['INFO']['SOR'])
        
        cursor.execute(query)
        connection.commit()
        # get the id of what just inserted
        cursor.execute('''SELECT LAST_INSERT_ID();''')
        results = cursor.fetchall()
        SNPID = results[0]
        # insert into snpeffect
        for allele in row['INFO']['ANN']:
            query = '''INSERT INTO snpeffect(SNPID,allele,effect,impact,gene_name,feature_type,transcript_biotype,ranktotal,HGVSc,HGVSp,cDNA_positioncDNA_length,Protein_positionProtein_length,warnings)
                        VALUES({},"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'''.format(SNPID,
                        allele.split('|')[0],
                        allele.split('|')[1],
                        allele.split('|')[2],
                        allele.split('|')[3],
                        allele.split('|')[5],
                        allele.split('|')[7],
                        allele.split('|')[8],
                        allele.split('|')[9],
                        allele.split('|')[10],
                        allele.split('|')[11],
                        allele.split('|')[13],
                        allele.split('|')[14])
            cursor.execute(query)
        connection.commit()
        # insert into have
        # get SID
        query = '''SELECT SID FROM sample WHERE EID = {} AND identifier = "{}"'''.format(EID,row['sample'])
        cursor.execute(query)
        results = cursor.fetchall()
        SID = results[0]
        query = '''INSERT INTO have(SID,SNPID,GT,GQ) VALUES({},{},"{}",{})'''.format(SID,SNPID,row['GT'],row['GQ'])
        cursor.execute(query)
        connection.commit()
    connection.close()
    
if __name__ == '__main__':
    df = read_vcf('Ros_FMNM_subset.snpeff.ann.ud0.vcf')
    print(df.head())
    print (len((get_samples(df))))
