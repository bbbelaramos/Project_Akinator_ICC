import os

def resetar_memoria():
    
    # Lista de arquivos para apagar
    arquivos = [
        os.path.join("data", "dados_bayes.csv"),
        os.path.join("data", "personagens.csv")
    ]
    
    print("🗑️  Iniciando limpeza...")
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"✅ Deletado: {arquivo}")
            except PermissionError:
                print(f"❌ Erro: O arquivo {arquivo} está aberto. Feche-o e tente novamente.")
        else:
            print(f"⚠️  Já estava apagado: {arquivo}")
            
    print("\n✨ Memória resetada com sucesso!")

if __name__ == "__main__":
    resp = input("Tem certeza que quer apagar TODO o aprendizado? (s/n): ").strip().lower()
    if resp == 's':
        resetar_memoria()
    else:
        print("Operação cancelada.")