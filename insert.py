import pandas as pd
import vcf

# this function parse a vcf files into lists containing essential infos
def read_vcf(vcf_file):
    reader = vcf.Reader(open(vcf_file))
    df = pd.DataFrame([vars(r) for r in reader])
    out = df.merge(pd.DataFrame(df.INFO.tolist()),
                   left_index=True, right_index=True)
    return out
    
if __name__ == '__main__':
    df = read_vcf('Ros_FMNM_subset.snpeff.ann.ud0.vcf')
    print(df)
