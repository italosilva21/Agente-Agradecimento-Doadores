"""
Serviço de geração de e-mails personalizados usando Google Gemini.
Utiliza IA para criar mensagens de agradecimento únicas para cada doador.
"""

from google import genai

import config


class AIService:
    """Gera e-mails personalizados de agradecimento usando Gemini."""

    def __init__(self):
        """Inicializa o cliente do Gemini."""
        self._client = genai.Client(api_key=config.GEMINI_API_KEY)

    def generate_thank_you_email(self, donor: dict) -> dict:
        """
        Gera um e-mail de agradecimento personalizado para o doador.

        Args:
            donor: Dicionário com os dados do doador (nome, valor, data_doacao, tipo_doacao).

        Returns:
            Dicionário com 'subject' (assunto) e 'body' (corpo em HTML).
        """
        prompt = self._build_prompt(donor)

        response = self._client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
        )

        # Extrai o texto gerado
        text = response.text.strip()

        # Faz parsing do assunto e corpo
        subject, body = self._parse_response(text, donor)

        return {
            "subject": subject,
            "body": body,
        }

    def _build_prompt(self, donor: dict) -> str:
        """Constrói o prompt para a IA gerar o e-mail."""
        return f"""Você é um especialista em comunicação institucional da organização "{config.ORGANIZATION_NAME}".

Crie um e-mail de agradecimento caloroso e profissional para um doador com as seguintes informações:

- **Nome do doador:** {donor['nome']}
- **Valor da doação:** R$ {donor['valor']}
- **Data da doação:** {donor['data_doacao']}
- **Forma de pagamento:** {donor['tipo_doacao']}

INSTRUÇÕES:
1. O e-mail deve ser em português brasileiro.
2. Seja caloroso, mas profissional. Não exagere.
3. Mencione o valor e agradeça de forma genuína.
4. Inclua uma breve menção ao impacto que a doação terá.
5. Use o nome do doador para personalizar a mensagem.
6. Assine como "{config.SENDER_NAME} — {config.ORGANIZATION_NAME}".

FORMATO OBRIGATÓRIO da resposta (siga exatamente):
ASSUNTO: [assunto do e-mail aqui]
---
[corpo do e-mail aqui, em texto simples com parágrafos separados por linhas em branco]
"""

    def _parse_response(self, text: str, donor: dict) -> tuple[str, str]:
        """
        Faz o parsing da resposta da IA, separando assunto e corpo.

        Returns:
            Tupla (assunto, corpo_html).
        """
        subject = f"Agradecimento pela sua doação — {config.ORGANIZATION_NAME}"
        body = text

        if "---" in text:
            parts = text.split("---", 1)
            subject_part = parts[0].strip()
            body = parts[1].strip()

            # Extrai o assunto
            for line in subject_part.split("\n"):
                line = line.strip()
                if line.upper().startswith("ASSUNTO:"):
                    subject = line.split(":", 1)[1].strip()
                    break

        # Converte o corpo para HTML simples
        body_html = self._text_to_html(body, donor)

        return subject, body_html

    def _text_to_html(self, text: str, donor: dict) -> str:
        """Converte o texto plano da IA em HTML formatado para e-mail."""
        # Divide em parágrafos
        paragraphs = text.split("\n\n")
        html_paragraphs = []

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            # Preserva quebras de linha dentro do parágrafo
            p = p.replace("\n", "<br>")
            html_paragraphs.append(f"<p>{p}</p>")

        body_content = "\n".join(html_paragraphs)

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
             max-width: 600px; margin: 0 auto; padding: 20px; 
             color: #333333; line-height: 1.6;">
    
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 24px;">
            💜 Obrigado, {donor['nome']}!
        </h1>
    </div>
    
    <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; 
                border-radius: 0 0 12px 12px;">
        {body_content}
    </div>
    
    <div style="text-align: center; padding: 20px; color: #888888; font-size: 12px;">
        <p>Este e-mail foi enviado por {config.ORGANIZATION_NAME}.</p>
    </div>
</body>
</html>"""
