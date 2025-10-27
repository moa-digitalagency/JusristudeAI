from backend.app import app
from backend.models.user import db, User
from backend.models.case import JurisprudenceCase
from backend.utils.encryption import encryption_service
from datetime import date

sample_cases = [
    {
        "case_number": "CA-2024-001",
        "title": "Responsabilité contractuelle - Défaut de livraison",
        "description": "Litige concernant la non-livraison de marchandises dans les délais convenus. Le vendeur invoque la force majeure due aux conditions météorologiques exceptionnelles.",
        "facts": "Le 15 janvier 2024, la société ABC a commandé 500 unités de matériel informatique auprès de la société XYZ. Le contrat stipulait une livraison au plus tard le 1er février 2024. Les marchandises n'ont été livrées que le 20 février 2024.",
        "decision": "La Cour rejette l'argument de la force majeure et condamne le vendeur à verser des dommages-intérêts pour le préjudice causé par le retard de livraison.",
        "court": "Cour d'appel de Paris",
        "date_decision": date(2024, 3, 15),
        "category": "Droit commercial",
        "keywords": "contrat, livraison, force majeure, dommages-intérêts"
    },
    {
        "case_number": "TGI-2024-045",
        "title": "Droit du travail - Licenciement abusif",
        "description": "Contestation d'un licenciement pour faute grave. L'employé soutient que les motifs invoqués sont insuffisants et que la procédure n'a pas été respectée.",
        "facts": "M. Dupont a été licencié pour faute grave le 10 février 2024 après avoir prétendument divulgué des informations confidentielles. L'employeur n'a pas convoqué l'employé à un entretien préalable dans les délais légaux.",
        "decision": "Le tribunal requalifie le licenciement en licenciement sans cause réelle et sérieuse et condamne l'employeur à verser une indemnité de 15 000 euros.",
        "court": "Tribunal de grande instance de Lyon",
        "date_decision": date(2024, 5, 20),
        "category": "Droit du travail",
        "keywords": "licenciement, faute grave, procédure, indemnités"
    },
    {
        "case_number": "CA-2024-067",
        "title": "Responsabilité civile - Accident de la circulation",
        "description": "Action en réparation suite à un accident de la route impliquant deux véhicules. Détermination des responsabilités et évaluation du préjudice corporel.",
        "facts": "Le 5 mars 2024, une collision s'est produite au carrefour de la rue Victor Hugo et de l'avenue de la République. Le conducteur du véhicule A n'a pas respecté le feu rouge, percutant le véhicule B.",
        "decision": "La Cour retient la responsabilité exclusive du conducteur du véhicule A et fixe l'indemnisation du préjudice corporel à 50 000 euros.",
        "court": "Cour d'appel de Bordeaux",
        "date_decision": date(2024, 6, 10),
        "category": "Responsabilité civile",
        "keywords": "accident, circulation, préjudice corporel, indemnisation"
    },
    {
        "case_number": "TJ-2024-123",
        "title": "Droit de la famille - Garde d'enfants",
        "description": "Litige concernant la garde des enfants suite à un divorce. Les deux parents demandent la garde exclusive.",
        "facts": "Mme Martin et M. Martin se sont séparés en janvier 2024. Ils ont deux enfants âgés de 8 et 10 ans. Chaque parent demande la garde exclusive en invoquant l'intérêt supérieur des enfants.",
        "decision": "Le tribunal prononce une garde alternée avec résidence principale chez la mère et un droit de visite élargi pour le père, incluant la moitié des vacances scolaires.",
        "court": "Tribunal judiciaire de Marseille",
        "date_decision": date(2024, 4, 25),
        "category": "Droit de la famille",
        "keywords": "divorce, garde d'enfants, résidence alternée, intérêt de l'enfant"
    },
    {
        "case_number": "CA-2024-089",
        "title": "Droit immobilier - Vice caché",
        "description": "Action en garantie des vices cachés suite à l'acquisition d'un bien immobilier présentant des défauts de construction non apparents lors de la vente.",
        "facts": "En juin 2023, Mme Leblanc a acquis une maison. Six mois après l'achat, d'importants problèmes d'humidité et d'infiltration d'eau sont apparus, causés par des défauts dans l'isolation.",
        "decision": "La Cour reconnaît l'existence de vices cachés et condamne le vendeur à prendre en charge les travaux de réparation estimés à 35 000 euros.",
        "court": "Cour d'appel de Toulouse",
        "date_decision": date(2024, 7, 5),
        "category": "Droit immobilier",
        "keywords": "vice caché, vente immobilière, garantie, réparation"
    },
    {
        "case_number": "TGI-2024-156",
        "title": "Droit pénal - Escroquerie",
        "description": "Poursuite pour escroquerie dans le cadre d'une opération d'investissement frauduleuse. Le prévenu a collecté des fonds auprès de plusieurs victimes en promettant des rendements irréalistes.",
        "facts": "Entre 2022 et 2023, M. Bernard a collecté plus de 200 000 euros auprès de 15 investisseurs en leur promettant un rendement de 20% par an sur un projet immobilier fictif.",
        "decision": "Le tribunal condamne le prévenu à 3 ans de prison ferme et au remboursement intégral des sommes perçues aux victimes.",
        "court": "Tribunal de grande instance de Nantes",
        "date_decision": date(2024, 8, 12),
        "category": "Droit pénal",
        "keywords": "escroquerie, fraude, investissement, restitution"
    },
    {
        "case_number": "CA-2024-201",
        "title": "Propriété intellectuelle - Contrefaçon de marque",
        "description": "Action en contrefaçon de marque déposée. La société plaignante reproche à la société défenderesse l'utilisation d'une marque similaire créant un risque de confusion.",
        "facts": "La société Alpha, titulaire de la marque 'TechPro' déposée en 2020, constate que la société Beta commercialise des produits sous la marque 'TekPro' dans le même secteur d'activité.",
        "decision": "La Cour constate la contrefaçon et ordonne à la société Beta de cesser l'utilisation de la marque 'TekPro' et de verser 80 000 euros de dommages-intérêts.",
        "court": "Cour d'appel de Paris",
        "date_decision": date(2024, 9, 1),
        "category": "Propriété intellectuelle",
        "keywords": "contrefaçon, marque, confusion, dommages-intérêts"
    },
    {
        "case_number": "TJ-2024-234",
        "title": "Droit de la consommation - Clause abusive",
        "description": "Contestation d'une clause contractuelle jugée abusive dans un contrat de service de télécommunication.",
        "facts": "Un opérateur de télécommunication a inclus dans ses contrats une clause permettant une augmentation unilatérale des tarifs sans limitation. L'association de consommateurs a saisi le tribunal.",
        "decision": "Le tribunal déclare la clause abusive et nulle, et condamne l'opérateur à rembourser les augmentations indues aux abonnés concernés.",
        "court": "Tribunal judiciaire de Lille",
        "date_decision": date(2024, 10, 5),
        "category": "Droit de la consommation",
        "keywords": "clause abusive, télécommunication, remboursement, protection du consommateur"
    }
]

with app.app_context():
    admin = User.query.filter_by(email='admin@jurisprudence.com').first()
    
    if admin:
        existing_cases = JurisprudenceCase.query.count()
        
        if existing_cases == 0:
            print("Ajout de cas de jurisprudence de démonstration...")
            
            for case_data in sample_cases:
                case = JurisprudenceCase(
                    case_number=case_data['case_number'],
                    title=case_data['title'],
                    description_encrypted=encryption_service.encrypt(case_data['description']),
                    facts_encrypted=encryption_service.encrypt(case_data['facts']),
                    decision_encrypted=encryption_service.encrypt(case_data['decision']),
                    court=case_data['court'],
                    date_decision=case_data['date_decision'],
                    category=case_data['category'],
                    keywords=case_data['keywords'],
                    created_by=admin.id
                )
                db.session.add(case)
            
            db.session.commit()
            print(f"✓ {len(sample_cases)} cas de jurisprudence ajoutés avec succès!")
        else:
            print(f"La base de données contient déjà {existing_cases} cas.")
    else:
        print("Erreur: Administrateur non trouvé")
