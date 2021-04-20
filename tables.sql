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
    SNPID int not null AUTO_INCREMENT,
    RPID int not null,
    alt_allele varchar(255) not null,
    qual decimal(10,4) not null,
    pass varchar(10) not null,
    AC int not null,
    AF decimal(6,5) not null,
    AN int not null,
    baseQRankSum decimal(6,4) not null,
    clippingRankSum decimal(6,4) not null,
    DP int not null,
    excessHet decimal(6,5) not null,
    FS decimal(6,5) not null,
    inbreedingCoeff decimal(6,5) not null,
    MLEAC int not null,
    MLEAF decimal(6,5) not null,
    MQ decimal(6,3) not null,
    MQRankSum decimal(6,5) not null,
    QD decimal(6,3) not null,
    readPosRankSum decimal(6,5) not null,
    SOR decimal(6,5) not null,
    PRIMARY KEY(SNPID),
    FOREIGN KEY(RPID) REFERENCES reference(RPID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

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
    allele varchar(1) not null,
    PRIMARY KEY(RPID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE gene (
    GID int not null AUTO_INCREMENT,
<<<<<<< Updated upstream
    chromosome_number int not null,
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
=======
    chromosome varchar(255) not null,
    start_position int not null,
    end_position int not null,
    name varchar(255) not null, 
    PRIMARY KEY(GID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
    
CREATE TABLE infucntion (
>>>>>>> Stashed changes
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
