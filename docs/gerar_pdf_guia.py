import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "Projeto Preditor de Redes — Guia Didático da Parte 2 (Árvore de Decisão)")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
        # Footer
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, page_text)
        self.drawString(54, 36, "Material de Apoio Interno — Grupo 5 | Estrutura de Dados II")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 8.5 * inch - 54, 48)
        self.restoreState()

def build_pdf(filename="docs/Guia_Parte2_Arvore_de_Decisao.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    c_primary = colors.HexColor("#1A365D")   # Deep navy
    c_secondary = colors.HexColor("#2B6CB0") # Vibrant blue
    c_dark = colors.HexColor("#2D3748")      # Charcoal body
    c_muted = colors.HexColor("#4A5568")     # Muted gray
    c_box_bg = colors.HexColor("#F7FAFC")    # Light background
    c_box_border = colors.HexColor("#CBD5E0")
    c_highlight = colors.HexColor("#C53030") # Alert/Overfitting
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        alignment=0,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=0,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    box_text_style = ParagraphStyle(
        'BoxText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark
    )

    box_code_style = ParagraphStyle(
        'BoxCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2C5282")
    )
    
    script_style = ParagraphStyle(
        'ScriptSpeech',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    # Title & Header
    story.append(Paragraph("Guia Didático da Parte 2: Árvore de Decisão", title_style))
    story.append(Paragraph("Teoria, Intuição, Aplicação em Redes e Roteiro de Apresentação", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=0, spaceAfter=12))

    # Meta Info Card
    meta_data = [
        [
            Paragraph("<b>Público-Alvo:</b> Estudantes de TI (foco em intuição antes da fórmula)", box_text_style),
            Paragraph("<b>Módulo:</b> Parte 2 — Teoria I (Árvore de Decisão)", box_text_style)
        ],
        [
            Paragraph("<b>Papel no Artigo:</b> Conceito-base supervisionado", box_text_style),
            Paragraph("<b>Tempo na Apresentação:</b> ~50 segundos", box_text_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Seção 1
    story.append(Paragraph("1. A Intuição: O que é uma Árvore de Decisão?", h1_style))
    story.append(Paragraph(
        "Pense no jogo <b>Akinator</b> ou em uma <b>triagem médica de pronto-socorro</b>. "
        "Quando um paciente chega com febre, o médico não chuta o diagnóstico; ele realiza perguntas sequenciais "
        "ordenadas por relevância: <i>'A temperatura está acima de 38°C?'</i>, <i>'Tem falta de ar?'</i>, <i>'Há dor de garganta?'</i>.",
        body_style
    ))
    story.append(Paragraph(
        "No Aprendizado de Máquina, a <b>Árvore de Decisão</b> opera com essa exata lógica sobre os pacotes de rede. "
        "Ela analisa as métricas da rota (como <code>z_robusto</code>, <code>perda_pct</code> e <code>jitter_relativo</code>) "
        "e estabelece uma sequência ótima de regras de 'Sim ou Não' para classificar o fluxo em <b>OK</b>, <b>RISCO</b> ou <b>FALHA</b>.",
        body_style
    ))

    # Seção 2
    story.append(Paragraph("2. Anatomia da Árvore (Terminologia Essencial)", h1_style))
    story.append(Paragraph("A estrutura é composta por quatro elementos principais:", body_style))
    story.append(Paragraph("• <b>Nó Raiz (Root Node):</b> O ponto de partida. Realiza a primeira pergunta, avaliando o atributo que mais separa o tráfego saudável das anomalias (em nosso projeto, o <code>z_robusto</code>).", bullet_style))
    story.append(Paragraph("• <b>Nós Internos (Decision Nodes):</b> Perguntas intermediárias que refinam o diagnóstico à medida que a árvore se aprofunda.", bullet_style))
    story.append(Paragraph("• <b>Ramos (Branches):</b> As bifurcações que conectam os nós, representando as respostas às condições (ex: <i>z_robusto &gt; 3.0 = Verdadeiro / Falso</i>).", bullet_style))
    story.append(Paragraph("• <b>Folhas (Leaf Nodes):</b> Os nós terminais da árvore. Não contêm mais perguntas; entregam a classe final predita (OK, RISCO ou FALHA).", bullet_style))

    # Diagrama em Box
    tree_ascii = (
        "                    [ NÓ RAIZ: z_robusto > 3.0? ]\n"
        "                           /            \\\n"
        "                  (Sim)   /              \\   (Não)\n"
        "                         /                \\\n"
        "      [ NÓ INTERNO: n5_risco > 2? ]     ( FOLHA: OK )\n"
        "              /             \\\n"
        "     (Sim)   /               \\   (Não)\n"
        "            /                 \\\n"
        "     ( FOLHA: FALHA )   ( FOLHA: RISCO )"
    )
    diagram_table = Table([[Paragraph(f"<pre>{tree_ascii}</pre>", box_code_style)]], colWidths=[500])
    diagram_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BEE3F8")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(diagram_table)
    story.append(Spacer(1, 8))

    # Seção 3
    story.append(Paragraph("3. Como a IA Escolhe a Pergunta? (Critérios de Pureza)", h1_style))
    story.append(Paragraph(
        "Como o computador decide qual pergunta fazer primeiro sem intervenção manual? "
        "Imagine uma urna com bolas verdes (OK), amarelas (RISCO) e vermelhas (FALHA) completamente misturadas. "
        "O objetivo da árvore é encontrar uma linha de corte que separe essas cores da forma mais uniforme possível.",
        body_style
    ))
    story.append(Paragraph(
        "Essa 'bagunça' ou grau de mistura de uma amostra é calculada por métricas estatísticas de <b>impureza</b>:",
        body_style
    ))
    story.append(Paragraph("• <b>Índice Gini:</b> Mede a probabilidade de um elemento ser classificado incorretamente caso receba um rótulo aleatório. Varia de 0 (pureza total, apenas uma classe no nó) a valores próximos de 0.5 ou mais (mistura total).", bullet_style))
    story.append(Paragraph("• <b>Entropia:</b> Baseada na Teoria da Informação de Shannon. Mede a desordem dos dados em bits. Entropia 0 indica pureza absoluta.", bullet_style))
    story.append(Paragraph(
        "O algoritmo testa exaustivamente todos os atributos e pontos de corte possíveis, escolhendo aquele que entrega o maior "
        "<b>Ganho de Informação</b> (a maior redução imediata da impureza).",
        body_style
    ))

    # Seção 4
    story.append(Paragraph("4. O Grande Perigo: Overfitting e Alta Variância", h1_style))
    story.append(Paragraph(
        "Se uma árvore de decisão puder crescer indefinidamente, ela continuará se ramificando até criar uma regra exclusiva "
        "para cada amostra específica da base de treino. O resultado é o <b>Overfitting (Superajuste)</b>: "
        "o modelo atinge 100% de acerto decorando o histórico, mas perde totalmente a capacidade de generalizar diante de dados reais futuros.",
        body_style
    ))
    story.append(Paragraph(
        "Dizemos que árvores isoladas sofrem de <b>Alta Variância</b> (pequenas perturbações no dataset de treino alteram completamente sua estrutura).",
        body_style
    ))
    story.append(Paragraph("<b>Mecanismos de Controle Aplicados no Projeto:</b>", body_style))
    story.append(Paragraph("• <b>Profundidade Máxima (<code>max_depth</code>):</b> Limita o número máximo de perguntas sequenciais (ex: profundidade 4 ou 5), forçando a árvore a captar apenas padrões amplos.", bullet_style))
    story.append(Paragraph("• <b>Poda (Pruning):</b> Remoção programada de ramos com baixo ganho discriminante, eliminando ramificações que atendem apenas a ruídos de rede.", bullet_style))

    # Seção 5
    story.append(Paragraph("5. Exemplo Prático com os Dados do Nosso Projeto", h1_style))
    story.append(Paragraph(
        "Considere um pacote trafegando na rota intercontinental <b>São Paulo ➔ Amsterdã</b> coletado via RIPE Atlas:",
        body_style
    ))
    
    ex_steps = [
        [Paragraph("<b>Passo 1 (Nó Raiz):</b>", box_text_style), Paragraph("A árvore pergunta: <code>z_robusto &gt; 3.0</code>? (A latência atual desviou mais de 3 desvios robustos da mediana histórica dessa rota?). Se <b>Não</b>, vai para folha <b>OK</b>.", box_text_style)],
        [Paragraph("<b>Passo 2 (Nó Interno):</b>", box_text_style), Paragraph("Se <b>Sim</b>, a árvore testa: <code>n5_risco &gt; 2</code>? (Dos últimos 5 pacotes dessa mesma rota, mais de 2 já exibiram comportamento anômalo?).", box_text_style)],
        [Paragraph("<b>Passo 3 (Folha Final):</b>", box_text_style), Paragraph("Se <b>Sim</b>, classifica como <b>FALHA</b> (degradação persistente). Se <b>Não</b>, classifica como <b>RISCO</b> (anomalia pontual ou jitter transitório).", box_text_style)]
    ]
    ex_table = Table(ex_steps, colWidths=[120, 380])
    ex_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(ex_table)
    story.append(Spacer(1, 8))

    # Seção 6
    story.append(Paragraph("6. Texto-Base Sugerido para o Artigo HTML/MD", h1_style))
    artigo_sugestao = (
        "<b>2.1 Árvore de Decisão: A Base do Diagnóstico Estruturado</b><br/><br/>"
        "A Árvore de Decisão fundamenta o aprendizado supervisionado deste trabalho através de um modelo intuitivo "
        "semelhante a um fluxograma hierárquico. Estruturada a partir de um <b>Nó Raiz</b>, <b>Nós Internos</b> de teste "
        "e <b>Folhas</b> com as categorias finais (OK, RISCO ou FALHA), a árvore particiona o espaço de atributos da rede "
        "avaliando o <i>Índice Gini</i> ou a <i>Entropia</i> para maximizar a pureza de cada divisão.<br/><br/>"
        "Sua principal vantagem operacional reside na <b>alta interpretabilidade</b> (modelo 'caixa-branca'), permitindo "
        "que engenheiros de infraestrutura auditem e validem visualmente os limites lógicos que acionam cada alarme. "
        "Entretanto, árvores sem restrição exibem alta variância e suscetibilidade severa ao <b>overfitting</b>. "
        "Em nosso pipeline, mitigamos essa fragilidade parametrizando a profundidade máxima (<code>max_depth</code>) "
        "via busca em grade (<i>GridSearchCV</i>), preservando a capacidade de generalização do modelo em novos fluxos."
    )
    artigo_table = Table([[Paragraph(artigo_sugestao, box_text_style)]], colWidths=[500])
    artigo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(artigo_table)
    story.append(Spacer(1, 10))

    # Seção 7
    story.append(Paragraph("7. Roteiro Cronometrado para a Apresentação Oral (~50 segundos)", h1_style))
    speech_text = (
        "<i>\"Olá a todos! Eu sou o responsável por apresentar a <b>Árvore de Decisão</b>, o alicerce comparativo da nossa pesquisa.<br/><br/>"
        "A Árvore funciona como um fluxograma lógico direto: diante de um pacote de rede, ela faz perguntas sequenciais de 'Sim ou Não'. "
        "Começamos pelo <b>nó raiz</b> com o teste mais relevante — no nosso caso, se o desvio relativo <code>z_robusto</code> superou o limiar —, "
        "percorremos os <b>ramos</b> e alcançamos as <b>folhas</b>, que entregam o veredito operacional: OK, Risco ou Falha.<br/><br/>"
        "Para eleger a pergunta ideal em cada estágio sem achismos, o algoritmo analisa o <b>Índice Gini</b>, identificando a divisão "
        "que mais reduz a incerteza e isola o tráfego anômalo.<br/><br/>"
        "Seu maior benefício é ser uma 'caixa-branca' 100% auditável por equipes de NOC e SRE. Por outro lado, árvores isoladas sofrem "
        "com facilidade de <b>overfitting</b>, decorando o ruído histórico. Por isso, limitamos sua profundidade máxima através do "
        "GridSearchCV, servindo de régua para compararmos com os modelos em conjunto que veremos a seguir.\"</i>"
    )
    speech_table = Table([[Paragraph(speech_text, script_style)]], colWidths=[500])
    speech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEFCBF")), # Soft yellow highlight
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#D69E2E")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(speech_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF gerado com sucesso: {filename}")

if __name__ == '__main__':
    build_pdf()
