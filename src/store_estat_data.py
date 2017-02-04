from SPARQLWrapper import SPARQLWrapper, JSON
from pymongo import MongoClient
from inspect import ismethod

MONGOHOST = "localhost:27017"
MONGODB = "lod_notebook"

client = MongoClient(MONGOHOST)
db_connect = client[MONGODB]
sparql = SPARQLWrapper('http://data.e-stat.go.jp/lod/sparql/query')


# 全てのSPARQLを実行し、mongodbへ取得した値を格納するには
# call_all_SPARQL(Store())
def call_all_SPARQL(obj):
    #get_area_code()
    for f in dir(obj):
        attr = getattr(obj, f)
        if ismethod(attr):
            attr()


def get_area_code():
    sparql.setQuery("""
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
        PREFIX cd-dimension-2016:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/2016/>
        PREFIX cd-code-2016:<http://data.e-stat.go.jp/lod/ontology/crossDomain/code/2016/>
        PREFIX pc-measure-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/measure/2010/>
        PREFIX pc-dimension-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/dimension/2010/>
        PREFIX pc-code-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/code/2010/>
        PREFIX ic:<http://imi.ipa.go.jp/ns/core/rdf#>
        select ?areacode ?jinko ?ken ?siku
        where {
              ?s pc-measure-2010:population ?jinko ;
                 cd-dimension:standardAreaCode ?areacode.
              ?s cd-dimension-2016:nationality cd-code-2016:nationality-japanese ;
                 cd-dimension-2016:sex cd-code-2016:sex-total ;
                 pc-dimension-2010:area pc-code-2010:area-all ;
                 cd-dimension-2016:age cd-code-2016:age-total .
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        area_data = {}
        area_data["_id"] = result["areacode"]["value"]
        area_data["total"] = result["jinko"]["value"]
        db_connect["area_data"].insert(area_data)


class Store:
    def test(self):
        sparql.setQuery("""
            PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            select ?areacode ?seizouhin_syukka
            where{
                ?s1 ssds-measure-2016:C3401 ?seizouhin_syukka ;
                    cd-dimension:standardAreaCode ?areacode .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        items = []
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            seizouhin_syukka = result["seizouhin_syukka"]["value"]
            updata = {"$set": {"area_code": area, "seizouhin_syukka": seizouhin_syukka}}
            print(updata)
            items.append(updata)

        print(len(items))

    # 都道府県名、市町村区名
    def get_area_name(self):
        sparql.setQuery("""
            PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ic:<http://imi.ipa.go.jp/ns/core/rdf#>
            select ?areacode ?pref ?city
            where {
                  ?areacode  ic:都道府県 ?pref ;
                        ic:市区町村 ?city .
            }
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area_code = result["areacode"]["value"]
            pref = result["pref"]["value"]
            city = result["city"]["value"]
            updata = {"$set": {"pref": pref, "city": city}}
            db_connect["area_data"].update({"_id": area_code}, updata)

    # 女性の人口
    def get_population_female(self):
        sparql.setQuery("""
            PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            PREFIX cd-dimension-2016:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/2016/>
            PREFIX cd-code-2016:<http://data.e-stat.go.jp/lod/ontology/crossDomain/code/2016/>
            PREFIX pc-measure-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/measure/2010/>
            PREFIX pc-dimension-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/dimension/2010/>
            PREFIX pc-code-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/code/2010/>
            PREFIX ic:<http://imi.ipa.go.jp/ns/core/rdf#>
            select ?areacode ?female
            where {
                  ?sf pc-measure-2010:population ?female ;
                     cd-dimension:standardAreaCode ?areacode.
                  ?sf cd-dimension-2016:nationality cd-code-2016:nationality-japanese ;
                     cd-dimension-2016:sex cd-code-2016:sex-female ;
                     pc-dimension-2010:area pc-code-2010:area-all ;
                     cd-dimension-2016:age cd-code-2016:age-total .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area_code = result["areacode"]["value"]
            female = result["female"]["value"]
            update = {"$set": {"p_female": female}}
            db_connect["area_data"].update({"_id": area_code}, update)

    # 男性の人口
    def get_population_male(self):
        sparql.setQuery("""
            PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            PREFIX cd-dimension-2016:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/2016/>
            PREFIX cd-code-2016:<http://data.e-stat.go.jp/lod/ontology/crossDomain/code/2016/>
            PREFIX pc-measure-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/measure/2010/>
            PREFIX pc-dimension-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/dimension/2010/>
            PREFIX pc-code-2010:<http://data.e-stat.go.jp/lod/ontology/populationCensus/code/2010/>
            PREFIX ic:<http://imi.ipa.go.jp/ns/core/rdf#>
            select ?areacode ?male
            where {
                  ?sf pc-measure-2010:population ?male ;
                     cd-dimension:standardAreaCode ?areacode.
                  ?sf cd-dimension-2016:nationality cd-code-2016:nationality-japanese ;
                     cd-dimension-2016:sex cd-code-2016:sex-male ;
                     pc-dimension-2010:area pc-code-2010:area-all ;
                     cd-dimension-2016:age cd-code-2016:age-total .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area_code = result["areacode"]["value"]
            male = result["male"]["value"]
            updata = {"$set": {"p_male": male}}
            db_connect["area_data"].update({"_id": area_code}, updata)

    # 保育所
    def get_hoikusyo(self):
        sparql.setQuery("""
            PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            select ?areacode ?hoikusyo ?jidou_taiki ?jidou_zaisyo
            where{
                ?s1 ssds-measure-2016:J2503 ?hoikusyo ;
                    cd-dimension:standardAreaCode ?areacode .
                ?s2 ssds-measure-2016:J250502 ?jidou_taiki ;
                    cd-dimension:standardAreaCode ?areacode .
                ?s3 ssds-measure-2016:J2506 ?jidou_zaisyo ;
                    cd-dimension:standardAreaCode ?areacode .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            hoikusyo = result["hoikusyo"]["value"]
            jidou_taiki = result["jidou_taiki"]["value"]
            jidou_zaisyo = result["jidou_zaisyo"]["value"]
            updata = {"$set": {"c_hoikusyo": hoikusyo, "c_jidou_taiki": jidou_taiki, "c_jidou_zaisyo": jidou_zaisyo}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 児童福祉施設
    def get_jidou_fukushi(self):
        sparql.setQuery("""
            PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            select ?areacode ?jidou_fukushi
            where{
                ?s ssds-measure-2016:J2501 ?jidou_fukushi ;
                    cd-dimension:standardAreaCode ?areacode .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            jidou_fukushi = result["jidou_fukushi"]["value"]
            updata = {"$set": {"c_jidou_fukushi": jidou_fukushi}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 幼稚園
    def get_yochien(self):
        sparql.setQuery("""
            PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            select ?areacode ?yochien ?yochien_zaien
            where{
                ?s1 ssds-measure-2016:E1101 ?yochien ;
                    cd-dimension:standardAreaCode ?areacode .
                ?s2 ssds-measure-2016:E1501 ?yochien_zaien ;
                    cd-dimension:standardAreaCode ?areacode .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            yochien = result["yochien"]["value"]
            yochien_zaien = result["yochien_zaien"]["value"]
            updata = {"$set": {"e_yochien": yochien, "e_yochien_zaien":yochien_zaien}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 小学校
    def get_syogakukou(self):
        sparql.setQuery("""
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?syogakukou ?syogaku_kyoin ?syogaku_jidou
                    where{
                        ?s1 ssds-measure-2016:E2101 ?syogakukou ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 ssds-measure-2016:E2401 ?syogaku_kyoin ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s3 ssds-measure-2016:E2501 ?syogaku_jidou ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            syogakukou = result["syogakukou"]["value"]
            syogaku_kyoin = result["syogaku_kyoin"]["value"]
            syogaku_jidou = result["syogaku_jidou"]["value"]
            updata = {"$set": { "e_syogakukou": syogakukou, "e_syogaku_kyoin": syogaku_kyoin,
                               "e_syogaku_jidou": syogaku_jidou}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 中学校
    def get_tyuugaku(self):
        sparql.setQuery("""
            PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            select ?areacode ?tyuugaku ?tyuugaku_seito ?tyuugaku_kyoin
            where{
                ?s1 ssds-measure-2016:E3101 ?tyuugaku ;
                    cd-dimension:standardAreaCode ?areacode .
                ?s2 ssds-measure-2016:E3501 ?tyuugaku_seito ;
                    cd-dimension:standardAreaCode ?areacode .
                ?s3 ssds-measure-2016:E3401 ?tyuugaku_kyoin ;
                    cd-dimension:standardAreaCode ?areacode .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            tyuugaku = result["tyuugaku"]["value"]
            tyuugaku_seito = result["tyuugaku_seito"]["value"]
            tyuugaku_kyoin = result["tyuugaku_kyoin"]["value"]
            updata = {"$set": {"e_tyuugaku": tyuugaku, "e_tyuugaku_seito":tyuugaku_seito, "e_tyuugaku_kyoin": tyuugaku_kyoin}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 高校
    def get_koukou(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?koukou ?koukou_seito
                    where{
                        ?s1 ssds-measure-2016:E4101 ?koukou ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 ssds-measure-2016:E4501 ?koukou_seito ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            koukou = result["koukou"]["value"]
            koukou_seito = result["koukou_seito"]["value"]
            updata = {"$set": {"e_koukou": koukou, "e_koukou_seito": koukou_seito}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 地方税
    def get_lacal_tax(self):
        sparql.setQuery("""
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
        PREFIX sds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
        select ?areacode ?local_tax
        where {
              ?s sds-measure-2016:D320101 ?local_tax ;
                 cd-dimension:standardAreaCode ?areacode .
        }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            local_tax = result["local_tax"]["value"]
            updata = {"$set": {"t_local_tax": local_tax}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 出生・死亡
    def get_syussei(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?syussei ?sibou
                    where{
                        ?s1 ssds-measure-2016:A4101 ?syussei ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 ssds-measure-2016:A4200 ?sibou ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            syussei = result["syussei"]["value"]
            sibou = result["sibou"]["value"]
            updata = {"$set": {"p_syussei": syussei, "p_sibou": sibou}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 婚姻・離婚
    def get_konin(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?konin ?rikon
                    where{
                        ?s1 ssds-measure-2016:A9101 ?konin ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 ssds-measure-2016:A9201 ?rikon ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            konin = result["konin"]["value"]
            rikon = result["rikon"]["value"]
            updata = {"$set": {"p_konin": konin, "p_rikon": rikon}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 医療
    def get_byoin(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?byoin ?sinryojyo ?ishi
                    where{
                        ?s1 ssds-measure-2016:I510120 ?byoin ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 ssds-measure-2016:I5102 ?sinryojyo ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s3 ssds-measure-2016:I6100 ?ishi ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            byoin = result["byoin"]["value"]
            sinryojyo = result["sinryojyo"]["value"]
            ishi = result["ishi"]["value"]
            updata = {"$set": {"m_byoin": byoin, "m_sinryojyo": sinryojyo, "m_ishi": ishi}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 介護
    def get_kaigo_sisetsu(self):
        sparql.setQuery("""
            PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
            select ?areacode ?kaigo_sisetsu
            where{
                ?s1 ssds-measure-2016:J230121 ?kaigo_sisetsu ;
                    cd-dimension:standardAreaCode ?areacode .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            kaigo_sisetsu = result["kaigo_sisetsu"]["value"]
            updata = {"$set": {"m_kaigo_sisetsu": kaigo_sisetsu}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 住民基本台帳人口移動
    def get_tennyuu(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX im-measure-2016:<http://data.e-stat.go.jp/lod/ontology/reportOnTheInternalMigrationInJapan/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?tennyuu ?tensyutsu
                    where{
                        ?s1 im-measure-2016:numberOfPeopleMovingInFromOtherMunicipalities ?tennyuu ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 im-measure-2016:numberOfPeopleMovingToOtherMunicipalities ?tensyutsu ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            tennyuu = result["tennyuu"]["value"]
            tensyutsu = result["tensyutsu"]["value"]
            updata = {"$set": {"p_tennyuu": tennyuu, "p_tensyutsu": tensyutsu}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 自市区町村の就業者・通勤している就業者
    def get_tuukin(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?jitiku_syuugyo ?tatikuhe_tuukin ?taikukara_tuukin
                    where{
                        ?s1 ssds-measure-2016:F2701 ?jitiku_syuugyo ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 ssds-measure-2016:F2705 ?tatikuhe_tuukin ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s3 ssds-measure-2016:F2803 ?taikukara_tuukin ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            jitiku_syuugyo = result["jitiku_syuugyo"]["value"]
            tatikuhe_tuukin = result["tatikuhe_tuukin"]["value"]
            taikukara_tuukin = result["taikukara_tuukin"]["value"]
            updata = {"$set": {"w_jitiku_syuugyo": jitiku_syuugyo, "w_tatikuhe_tuukin": tatikuhe_tuukin,
                               "w_taikukara_tuukin": taikukara_tuukin}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 小売業
    def get_kouri(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?kouriten ?oogata_kouriten
                    where{
                        ?s1 ssds-measure-2016:H6130 ?kouriten ;
                            cd-dimension:standardAreaCode ?areacode .
                        ?s2 ssds-measure-2016:H6132 ?oogata_kouriten ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            kouriten = result["kouriten"]["value"]
            oogata_kouriten = result["oogata_kouriten"]["value"]
            updata = {"$set": {"i_kouriten": kouriten, "i_oogata_kouriten": oogata_kouriten}}
            db_connect["area_data"].update({"_id": area}, updata)

        sparql.setQuery("""
                            PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                            PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                            select ?areacode ?hyakkaten ?insyokuten
                            where{
                                ?s3 ssds-measure-2016:H6133 ?hyakkaten ;
                                    cd-dimension:standardAreaCode ?areacode .
                                ?s4 ssds-measure-2016:H6131 ?insyokuten ;
                                    cd-dimension:standardAreaCode ?areacode .
                            }
                        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            hyakkaten = result["hyakkaten"]["value"]
            insyokuten = result["insyokuten"]["value"]
            updata = {"$set": {"i_hyakkaten": hyakkaten, "i_insyokuten": insyokuten}}
            db_connect["area_data"].update({"_id": area}, updata)

    # 製造品出荷額等
    def get_seizouhin(self):
        sparql.setQuery("""
                    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ssds-measure-2016:<http://data.e-stat.go.jp/lod/ontology/systemOfSocialAndDemographicStatistics/measure/2016/>
                    PREFIX cd-dimension:<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/>
                    select ?areacode ?seizouhin_syukka
                    where{
                        ?s1 ssds-measure-2016:C3401 ?seizouhin_syukka ;
                            cd-dimension:standardAreaCode ?areacode .
                    }
                """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            area = result["areacode"]["value"]
            seizouhin_syukka = result["seizouhin_syukka"]["value"]
            updata = {"$set": {"i_seizouhin_syukka": seizouhin_syukka}}
            db_connect["area_data"].update({"_id": area}, updata)

if __name__ == '__main__':
    call_all_SPARQL(Store())
