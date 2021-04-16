import pandas as pd
import vcf
import pymysql

# a vcf parser to pandas pd
def read_vcf(vcf_file):
    vcf_reader = vcf.Reader(open(vcf_file))
    res=[]
    cols = ['sample','REF','ALT','GQ','chrom',
             'var_type','sub_type','start','end','QUAL','INFO']

    for rec in vcf_reader:
        x = [rec.CHROM, rec.var_type, rec.var_subtype, rec.start, rec.end, rec.QUAL, rec.INFO]
        for sample in rec.samples:
            if sample.gt_bases == None:
                #no call
                mut=''
                row = [sample.sample, rec.REF, sample.gt_bases, 0]
            elif rec.REF != sample.gt_bases:
                mut = str(rec.end)+rec.REF+'>'+sample.gt_bases
                cdata = sample.data
                row = [sample.sample, rec.REF, sample.gt_bases, cdata[3]
                      ] + x
            else:
                #call is REF
                mut = str(rec.end)+rec.REF              
                cdata = sample.data
                row = [sample.sample, rec.REF, sample.gt_bases, cdata[3],
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
    
# a huge insert, update all tables except goterm at one time
def insert(df, enotes, pdic, ):
    # order of insert, experiment(one time), population(in a loop), sample(in a loop), reference(in a loop), snp (huge loop), gene (in a loop), associate(in a loop), infunction(in a loop)
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
    
    
if __name__ == '__main__':
    df = read_vcf('Ros_FMNM_subset.snpeff.ann.ud0.vcf')
    print(df.head())
    print (len((get_samples(df))))
