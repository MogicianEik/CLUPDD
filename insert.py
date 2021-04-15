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
    
    
def insert_experiment(enotes): #TODO: make it mandatory on the html page
    connection = pymysql.connect(db='group_C', user='test',
                       passwd='test',
                       port = 4253)
    with connection.cursor() as cursor:
        query = "INSERT INTO experiment(notes) VALUES ('{}')".format(notes)
        cursor.execute(query)
        connection.commit()
        cursor.close()
    connection.close()

def insert_population(notes): #TODO: make it mandatory on the html page
    connection = pymysql.connect(db='group_C', user='test',
                       passwd='test',
                       port = 4253)
    with connection.cursor() as cursor:
        query = "INSERT INTO experiment(notes) VALUES ('{}')".format(notes)
        cursor.execute(query)
        connection.commit()
        cursor.close()
    connection.close()
    
def insert_sample(identifier, enotes, pname, notes=''):
    query1 = "SELECT PID FROM population WHERE name = '{}';".format(pname)
    connection = pymysql.connect(db='group_C', user='test',
                       passwd='test',
                       port = 4253)
    with connection.cursor() as cursor:
        cursor.execute(query1)
        results = cursor.fetchall()
        PID = results[0]
        query2 = "INSERT INTO sample(PID, EID, identifier, notes) VALUES ({},{},'{}','{}')".format(PID,EID,identifier,notes)
        cursor.execute(query2)
        connection.commit()
        cursor.close()
    connection.close()
    
# return insert querys TODO: on html cgi, check repeat insertion with the exsisiting data base, dump the repeat ones
def get_go_terms(go_file):
    terms = []
    infile = open(go_file,'r')
    for line in infile.readlines():
        gos = line.split()[1]
        go = gos.split(',')
        for g in go:
            terms.append(g)
    return list(set(terms))
    
    
def insert_goterm(terms):
    connection = pymysql.connect(db='group_C', user='test',
                       passwd='test',
                       port = 4253)
    with connection.cursor() as cursor:
        for term in terms:
            query = "INSERT INTO goterm(name) VALUES ('{}')".format(term)
            cursor.execute(query)
        connection.commit()
        cursor.close()
    connection.close()
    
if __name__ == '__main__':
    df = read_vcf('Ros_FMNM_subset.snpeff.ann.ud0.vcf')
    print(df.head())
    print (len((get_samples(df))))
