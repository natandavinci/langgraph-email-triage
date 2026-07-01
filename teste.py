# Importando o Estado e os Agentes POO
from graph.state import GraphState
from agents.finance_agent import FinanceAgent
from agents.support_agent import SupportAgent
from agents.commercial_agent import CommercialAgent
from agents.fallback_agent import FallbackAgent

print("🧪 [DEBUG SISTEMA]: Inicializando Ambiente de Testes Diretos dos Agentes...")

# 1. Instanciando as classes dos agentes especialistas
finance = FinanceAgent()
support = SupportAgent()
commercial = CommercialAgent()
fallback = FallbackAgent()

# 2. Massa de dados para simular os e-mails reais do cliente
casos_de_teste = [
    {
        "nome": "💰 CASO 1: FINANCEIRO (Cobrança Duplicada)",
        "agente": finance,
        "dados": {
            "sender_email": "rodrigo_finance@email.com",
            "body_email": "Fui cobrado duas vezes na fatura desse mês. Podem resolver e me devolver o dinheiro?",
            "urgency": "High", "sentiment": "Angry", "account_level": "Free", "history": []
        }
    },
    {
        "nome": "🛠️ CASO 2: SUPORTE TÉCNICO (Instabilidade)",
        "agente": support,
        "dados": {
            "sender_email": "thiago_dev@email.com",
            "body_email": "O sistema caiu e estou tendo instabilidade para acessar o dashboard de produção. Ajuda!",
            "urgency": "Critical", "sentiment": "Anxious", "account_level": "VIP", "history": []
        }
    },
    {
        "nome": "🤝 CASO 3: COMERCIAL (Proposta de Negócios)",
        "agente": commercial,
        "dados": {
            "sender_email": "diretor_empresa@partner.com",
            "body_email": "Olá, tenho interesse em fechar uma parceria de licenças em lote para 50 funcionários. Qual o orçamento?",
            "urgency": "Medium", "sentiment": "Neutral", "account_level": "VIP", "history": []
        }
    },
    {
        "nome": "🚨 CASO 4: FALLBACK (Contingência/Erro de Triagem)",
        "agente": fallback,
        "dados": {
            "sender_email": "aleatorio@email.com",
            "body_email": "Mensagem confusa que caiu no nó de erro de roteamento.",
            "urgency": "Low", "sentiment": "Neutral", "account_level": "Free", "history": []
        }
    }
]

# 3. Execução direta dos métodos das classes
for caso in casos_de_teste:
    print(f"\n==================================================")
    print(caso["nome"])
    print(f"==================================================")
    
    # Executa a inteligência do agente diretamente passando o dicionário de estado
    resultado = caso["agente"].answer(caso["dados"])
    
    print("\n🤖 [RESPOSTA DA IA]:")
    print(resultado.get("final_answer"))
    print("\n📥 [HISTÓRICO GERADO]:")
    for m in resultado.get("history", []):
        print(f"- {type(m).__name__}: {m.content[:60]}...")