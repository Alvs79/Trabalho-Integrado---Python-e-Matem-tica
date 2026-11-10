import pandas as pd
import numpy as np

def criar_base_curso_superior():
    np.random.seed(42)
    anos = list(range(2016, 2026))
    estados = [
        {"UF": "SP", "Estado": "São Paulo", "Regiao": "Sudeste", "Base_Taxa": 23.5},
        {"UF": "MG", "Estado": "Minas Gerais", "Regiao": "Sudeste", "Base_Taxa": 17.8},
        {"UF": "ES", "Estado": "Espírito Santo", "Regiao": "Sudeste", "Base_Taxa": 18.5},
        {"UF": "RJ", "Estado": "Rio de Janeiro", "Regiao": "Sudeste", "Base_Taxa": 22.8},
        {"UF": "PR", "Estado": "Paraná", "Regiao": "Sul", "Base_Taxa": 20.4},
        {"UF": "MS", "Estado": "Mato Grosso do Sul", "Regiao": "Centro-Oeste", "Base_Taxa": 19.1},
    ]
    
    areas = [
        {"Area": "Exatas / STEM", "Curso": "Engenharia de Software e TI", "Prop_Mulheres": 0.21},
        {"Area": "Exatas / STEM", "Curso": "Engenharia Civil e Produção", "Prop_Mulheres": 0.34},
        {"Area": "Humanas", "Curso": "Pedagogia e Licenciaturas", "Prop_Mulheres": 0.78},
        {"Area": "Humanas", "Curso": "Direito e Administração", "Prop_Mulheres": 0.56},
        {"Area": "Saúde", "Curso": "Medicina e Enfermagem", "Prop_Mulheres": 0.71},
    ]

    registros = []
    for ano in anos:
        fator_tempo = (ano - 2016) * 0.48
        for uf_info in estados:
            for area_info in areas:
                for sexo in ["Feminino", "Masculino"]:
                    prop_sexo = area_info["Prop_Mulheres"] if sexo == "Feminino" else (1 - area_info["Prop_Mulheres"])
                    if area_info["Area"] == "Exatas / STEM" and sexo == "Feminino":
                        prop_sexo += (ano - 2016) * 0.005
                    elif area_info["Area"] == "Exatas / STEM" and sexo == "Masculino":
                        prop_sexo -= (ano - 2016) * 0.005

                    escala_uf = {"SP": 45000, "MG": 22000, "RJ": 19000, "PR": 16000, "ES": 6500, "MS": 5200}[uf_info["UF"]]
                    ingressantes = int(escala_uf * prop_sexo * np.random.uniform(0.92, 1.08))
                    
                    taxa_conclusao_base = uf_info["Base_Taxa"] + fator_tempo
                    if area_info["Area"] == "Exatas / STEM":
                        taxa_conclusao = taxa_conclusao_base * np.random.uniform(0.75, 0.88)
                    else:
                        taxa_conclusao = taxa_conclusao_base * np.random.uniform(0.95, 1.12)

                    if uf_info["UF"] == "SP" and ano >= 2024 and area_info["Curso"] == "Engenharia de Software e TI":
                        taxa_conclusao *= 1.48
                    if uf_info["UF"] == "ES" and ano == 2020 and area_info["Area"] == "Exatas / STEM":
                        taxa_conclusao *= 0.45

                    concluintes = int(ingressantes * (taxa_conclusao / 100.0) * 2.2)

                    registros.append({
                        "Ano": ano,
                        "UF": uf_info["UF"],
                        "Estado": uf_info["Estado"],
                        "Regiao": uf_info["Regiao"],
                        "Area_Conhecimento": area_info["Area"],
                        "Curso": area_info["Curso"],
                        "Sexo": sexo,
                        "Ingressantes": ingressantes,
                        "Concluintes": concluintes,
                        "Taxa_Conclusao_Superior_Pct": round(taxa_conclusao, 2)
                    })

    df = pd.DataFrame(registros)
    df.to_csv("dados_curso_superior_ibge.csv", index=False, encoding="utf-8-sig")
    return df

if __name__ == "__main__":
    criar_base_curso_superior()
    print("Base dados_curso_superior_ibge.csv criada com sucesso!")
