﻿--------------------------------------------------------
--  File created - Monday-June-19-2017
--------------------------------------------------------
--------------------------------------------------------
--  DDL for Table CARS
--------------------------------------------------------

  CREATE TABLE "CARS"
   (	"ID" NUMBER GENERATED ALWAYS AS IDENTITY MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE  NOKEEP  NOSCALE ,
	"NUM" NVARCHAR2(32),
	"COLOR" NUMBER(*,0),
	"MARK" NVARCHAR2(256),
	"IS_FOREIGN" NUMBER(1,0)
   ) ;

   COMMENT ON COLUMN "CARS"."ID" IS 'identifier';
   COMMENT ON COLUMN "CARS"."NUM" IS 'license plate';
   COMMENT ON COLUMN "CARS"."COLOR" IS 'color in RGBA(8,8,8,8)';
   COMMENT ON COLUMN "CARS"."MARK" IS 'model';
   COMMENT ON COLUMN "CARS"."IS_FOREIGN" IS 'is imported flag';
--------------------------------------------------------
--  DDL for Table MASTERS
--------------------------------------------------------

  CREATE TABLE "MASTERS"
   (	"ID" NUMBER GENERATED ALWAYS AS IDENTITY MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE  NOKEEP  NOSCALE ,
	"NAME" NVARCHAR2(256)
   ) ;
--------------------------------------------------------
--  DDL for Table SERVICES
--------------------------------------------------------

  CREATE TABLE "SERVICES"
   (	"ID" NUMBER GENERATED ALWAYS AS IDENTITY MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE  NOKEEP  NOSCALE ,
	"NAME" NVARCHAR2(256),
	"COST_OUR" NUMBER,
	"COST_FOREIGN" NUMBER
   ) ;
--------------------------------------------------------
--  DDL for Table TEST
--------------------------------------------------------

  CREATE TABLE "TEST"
   (	"ID" NUMBER GENERATED ALWAYS AS IDENTITY MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE  NOKEEP  NOSCALE
   ) ;
--------------------------------------------------------
--  DDL for Table WORKS
--------------------------------------------------------

  CREATE TABLE "WORKS"
   (	"ID" NUMBER GENERATED ALWAYS AS IDENTITY MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE  NOKEEP  NOSCALE ,
	"DATE_WORK" DATE,
	"MASTER_ID" NUMBER,
	"CAR_ID" NUMBER,
	"SERVICE_ID" NUMBER
   ) ;
--------------------------------------------------------
--  DDL for Index CARS_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "CARS_PK" ON "CARS" ("ID")
  ;
--------------------------------------------------------
--  DDL for Index MASTERS_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "MASTERS_PK" ON "MASTERS" ("ID")
  ;
--------------------------------------------------------
--  DDL for Index SERVICES_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "SERVICES_PK" ON "SERVICES" ("ID")
  ;
--------------------------------------------------------
--  DDL for Index WORKS_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "WORKS_PK" ON "WORKS" ("ID")
  ;
--------------------------------------------------------
--  DDL for Index TEST_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "TEST_PK" ON "TEST" ("ID")
  ;
--------------------------------------------------------
--  Constraints for Table TEST
--------------------------------------------------------

  ALTER TABLE "TEST" MODIFY ("ID" NOT NULL ENABLE);
  ALTER TABLE "TEST" ADD CONSTRAINT "TEST_PK" PRIMARY KEY ("ID")
  USING INDEX  ENABLE;
--------------------------------------------------------
--  Constraints for Table MASTERS
--------------------------------------------------------

  ALTER TABLE "MASTERS" MODIFY ("ID" NOT NULL ENABLE);
  ALTER TABLE "MASTERS" MODIFY ("NAME" NOT NULL ENABLE);
  ALTER TABLE "MASTERS" ADD CONSTRAINT "MASTERS_PK" PRIMARY KEY ("ID")
  USING INDEX  ENABLE;
--------------------------------------------------------
--  Constraints for Table CARS
--------------------------------------------------------

  ALTER TABLE "CARS" MODIFY ("ID" NOT NULL ENABLE);
  ALTER TABLE "CARS" MODIFY ("NUM" NOT NULL ENABLE);
  ALTER TABLE "CARS" MODIFY ("COLOR" NOT NULL ENABLE);
  ALTER TABLE "CARS" MODIFY ("MARK" NOT NULL ENABLE);
  ALTER TABLE "CARS" MODIFY ("IS_FOREIGN" NOT NULL ENABLE);
  ALTER TABLE "CARS" ADD CONSTRAINT "CARS_PK" PRIMARY KEY ("ID")
  USING INDEX  ENABLE;
--------------------------------------------------------
--  Constraints for Table WORKS
--------------------------------------------------------

  ALTER TABLE "WORKS" MODIFY ("ID" NOT NULL ENABLE);
  ALTER TABLE "WORKS" MODIFY ("DATE_WORK" NOT NULL ENABLE);
  ALTER TABLE "WORKS" MODIFY ("MASTER_ID" NOT NULL ENABLE);
  ALTER TABLE "WORKS" MODIFY ("CAR_ID" NOT NULL ENABLE);
  ALTER TABLE "WORKS" MODIFY ("SERVICE_ID" NOT NULL ENABLE);
  ALTER TABLE "WORKS" ADD CONSTRAINT "WORKS_PK" PRIMARY KEY ("ID")
  USING INDEX  ENABLE;

  ALTER TABLE "WORKS" ADD CONSTRAINT WORKS_CARS_FK FOREIGN KEY ( CAR_ID ) REFERENCES "CARS" ( ID ) ON
  DELETE CASCADE NOT DEFERRABLE ;

  ALTER TABLE "WORKS" ADD CONSTRAINT WORKS_MASTERS_FK FOREIGN KEY ( MASTER_ID ) REFERENCES "MASTERS" ( ID ) ON
  DELETE CASCADE NOT DEFERRABLE ;

  ALTER TABLE "WORKS" ADD CONSTRAINT WORKS_SERVICES_FK FOREIGN KEY ( SERVICE_ID ) REFERENCES "SERVICES" ( ID ) ON
  DELETE CASCADE NOT DEFERRABLE ;
--------------------------------------------------------
--  Constraints for Table SERVICES
--------------------------------------------------------

  ALTER TABLE "SERVICES" MODIFY ("ID" NOT NULL ENABLE);
  ALTER TABLE "SERVICES" MODIFY ("NAME" NOT NULL ENABLE);
  ALTER TABLE "SERVICES" MODIFY ("COST_OUR" NOT NULL ENABLE);
  ALTER TABLE "SERVICES" MODIFY ("COST_FOREIGN" NOT NULL ENABLE);
  ALTER TABLE "SERVICES" ADD CONSTRAINT "SERVICES_PK" PRIMARY KEY ("ID")
  USING INDEX  ENABLE;
