CREATE TABLE experiment (
    EID int not null AUTO_INCREMENT,
    notes varchar(255),
    PRIMARY KEY(EID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE population (
    PID int not null AUTO_INCREMENT,
    name varchar(255) not null,
    PRIMARY KEY(PID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE goterm (
    GOID int not null AUTO_INCREMENT,
    name varchar(255) not null,
    description varchar(500) not null,
    PRIMARY KEY(GOID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE sample (
    SID int not null AUTO_INCREMENT,
    PID int not null,
    EID int not null,
    identifier varchar(255) not null,
    notes varchar(500),
    PRIMARY KEY(SID),
    FOREIGN KEY(PID) REFERENCES population(PID),
    FOREIGN KEY(EID) REFERENCES experiment(EID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE snp (
  SNPID int(11) NOT NULL AUTO_INCREMENT,
  RPID int(11) NOT NULL,
  alt_allele varchar(255) NOT NULL,
  qual decimal(12,5) NOT NULL,
  filter varchar(255) DEFAULT NULL,
  AC int(11) NOT NULL,
  AF decimal(6,5) NOT NULL,
  AN int(11) NOT NULL,
  baseQRankSum decimal(12,5) NOT NULL,
  clippingRankSum decimal(12,5) NOT NULL,
  DP int(11) NOT NULL,
  excessHet decimal(12,5) NOT NULL,
  FS decimal(12,5) NOT NULL,
  inbreedingCoeff decimal(12,5) NOT NULL,
  MLEAC int(11) NOT NULL,
  MLEAF decimal(12,5) NOT NULL,
  MQ decimal(12,3) NOT NULL,
  MQRankSum decimal(12,5) NOT NULL,
  QD decimal(12,5) NOT NULL,
  readPosRankSum decimal(12,5) NOT NULL,
  SOR decimal(12,5) NOT NULL,
  PRIMARY KEY (SNPID),
  KEY RPID (RPID),
  CONSTRAINT `snp_ibfk_1` FOREIGN KEY (`RPID`) REFERENCES `reference` (`RPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE snpeffect(
    SEID int AUTO_INCREMENT not null,
    SNPID int not null,
    allele varchar(255) not null,
    effect varchar(255) not null,
    impact enum('HIGH','LOW','MODERATE','MODIFIER') not null,
    gene_name varchar(255) not null,
    feature_type varchar(255) not null,
    transcript_biotype varchar(255) not null,
    ranktotal varchar(9) not null,
    HGVSc varchar(255) not null,
    HGVSp varchar(255) not null,
    cDNA_positioncDNA_length varchar(100) not null,
    Protein_positionProtein_length varchar(100) not null,
    warnings varchar(255),
    PRIMARY KEY(SEID),
    FOREIGN KEY(SNPID) REFERENCES snp(SNPID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE have (
    SID int not null,
    SNPID int not null,
    GT varchar(3) not null,
    GQ int not null,
    PRIMARY KEY(SNPID,SID),
    FOREIGN KEY (SNPID) REFERENCES snp(SNPID),
    FOREIGN KEY (SID) REFERENCES sample(SID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE reference (
    RPID int not null AUTO_INCREMENT,
    chromosome varchar(255) not null,
    position int not null,
    allele varchar(255) not null,
    PRIMARY KEY(RPID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE gene (
    GID int not null AUTO_INCREMENT,
    chromosome varchar(255) not null,
    start_position int not null,
    end_position int not null,
    feature_type varchar(255) not null,
    id varchar(255) not null,
    name varchar(255) not null,
    symbol varchar(255),
    parent varchar(255),
    owner varchar(255),
    PRIMARY KEY(GID)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE infunction (
    chromosome varchar(255) not null,
    start_position int not null,
    end_position int not null,
    name varchar(255) not null,
    PRIMARY KEY(GID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE infucntion (
    IFID int not null AUTO_INCREMENT,
    GOID int not null,
    GID int,
    PRIMARY KEY(IFID),
    FOREIGN KEY(GOID) REFERENCES goterm(GOID),
    FOREIGN KEY(GID) REFERENCES gene(GID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE associate (
    AID int not null AUTO_INCREMENT,
    RPID int,
    GID int,
    PRIMARY KEY(AID),
    FOREIGN KEY(RPID) REFERENCES reference(RPID),
    FOREIGN KEY(GID) REFERENCES gene(GID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
