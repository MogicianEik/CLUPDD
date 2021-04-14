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
    SID int not null,
    RPID int not null,
    allele varchar(255) not null,
    confidence int not null,
    effect varchar(255), # snp effect
    description varchar(255), # other info
    PRIMARY KEY(SNPID),
    FOREIGN KEY(SID) REFERENCES sample(SID),
    FOREIGN KEY(RPID) REFERENCES reference(RPID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
    
CREATE TABLE reference (
    RPID int not null AUTO_INCREMENT,
    chromosome varchar(4) not null,
    position int not null,
    allele varchar(1) not null,
    PRIMARY KEY(RPID)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE gene (
        GID int not null AUTO_INCREMENT,
    	chromosome_number int not null,
        organism varchar(255) not null,
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
