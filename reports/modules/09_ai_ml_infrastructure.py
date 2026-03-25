"""
Module 09: AI/ML Infrastructure
Thesis: OpenAI dominates the LLM layer; voice AI (Twilio+ElevenLabs) is the emerging stack.
"""
import matplotlib.pyplot as plt
import json
from collections import Counter
from .base_module import BaseModule
from . import theme


class AIMLInfrastructure(BaseModule):
    slug = "09_ai_ml_infrastructure"
    title = "AI/ML Infrastructure"
    subtitle = "LLM providers, vector databases, and the emerging AI tech stack"

    def _detect_ai(self):
        d = self.data
        ai_keywords = ['ai', 'ml', 'llm', 'machine learning', 'artificial intelligence', 'neural',
                        'deep learning', 'nlp', 'gpt', 'language model', 'generative']
        ai_vendors_keywords = ['openai', 'anthropic', 'cohere', 'hugging', 'pinecone', 'weaviate',
                                'elevenlabs', 'fixie', 'llama', 'baseten', 'modal', 'replicate',
                                'gemini', 'vertex', 'bedrock', 'perplexity']

        ai_companies = set()
        ai_vendor_counts = Counter()
        llm_providers = Counter()
        voice_ai = Counter()
        vector_dbs = Counter()

        for e in d['extracts']:
            doc_id = e['doc_id']
            overview = str(e.get('system_description', '')).lower() + ' ' + str(e.get('product', '')).lower()
            vendors_raw = e.get('third_party_services')
            if isinstance(vendors_raw, str):
                try: vendors_raw = json.loads(vendors_raw)
                except: vendors_raw = []

            is_ai = any(kw in overview for kw in ai_keywords)
            vendor_names = [v.get('vendor','').lower() for v in (vendors_raw or []) if isinstance(v, dict)]

            if any(kw in ' '.join(vendor_names) for kw in ai_vendors_keywords):
                is_ai = True

            if is_ai:
                ai_companies.add(doc_id)

            for vname in vendor_names:
                if 'openai' in vname: llm_providers['OpenAI'] += 1; ai_vendor_counts['OpenAI'] += 1
                if 'anthropic' in vname: llm_providers['Anthropic'] += 1; ai_vendor_counts['Anthropic'] += 1
                if 'gemini' in vname or 'vertex' in vname: llm_providers['Google (Gemini/Vertex)'] += 1; ai_vendor_counts['Google AI'] += 1
                if 'cohere' in vname: llm_providers['Cohere'] += 1
                if 'perplexity' in vname: llm_providers['Perplexity'] += 1
                if 'llama' in vname or 'fixie' in vname: llm_providers['Self-hosted (Llama)'] += 1
                if 'elevenlabs' in vname: voice_ai['ElevenLabs'] += 1; ai_vendor_counts['ElevenLabs'] += 1
                if 'twilio' in vname: voice_ai['Twilio'] += 1
                if 'pinecone' in vname: vector_dbs['Pinecone'] += 1
                if 'weaviate' in vname: vector_dbs['Weaviate'] += 1
                if 'qdrant' in vname: vector_dbs['Qdrant'] += 1

        return ai_companies, ai_vendor_counts, llm_providers, voice_ai, vector_dbs

    def generate_charts(self):
        d = self.data
        df, N = d['df'], d['N']
        ai_companies, ai_vendors, llm, voice, vectors = self._detect_ai()

        # AI company percentage
        fig, ax = plt.subplots(figsize=(8, 5))
        vals = [len(ai_companies), N - len(ai_companies)]
        ax.pie(vals, labels=[f'AI/ML Companies\n({len(ai_companies)})', f'Other\n({N-len(ai_companies)})'],
               autopct='%1.0f%%', colors=[theme.PURPLE, theme.MUTED],
               textprops={'color': theme.TEXT, 'fontsize': 12})
        ax.set_title('AI/ML Companies in Portfolio', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'ai_share')

        # LLM providers
        if llm:
            top_llm = llm.most_common(8)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.barh([l[0] for l in top_llm][::-1], [l[1] for l in top_llm][::-1], color=theme.PURPLE, height=0.6)
            for i, v in enumerate([l[1] for l in top_llm][::-1]):
                ax.text(v + 0.3, i, str(v), va='center', fontsize=11)
            ax.set_xlabel('Companies Using')
            ax.set_title('LLM Provider Landscape', fontsize=14, fontweight='bold')
            self.save_chart(fig, 'llm_providers')

        # AI vendor landscape
        if ai_vendors:
            top_ai = ai_vendors.most_common(12)
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.barh([a[0] for a in top_ai][::-1], [a[1] for a in top_ai][::-1], color=theme.BLUE, height=0.6)
            for i, v in enumerate([a[1] for a in top_ai][::-1]):
                ax.text(v + 0.3, i, str(v), va='center', fontsize=10)
            ax.set_xlabel('Companies')
            ax.set_title('AI/ML Vendor Ecosystem', fontsize=14, fontweight='bold')
            self.save_chart(fig, 'ai_vendors')

    def generate_narrative(self):
        d = self.data
        N = d['N']
        ai_companies, ai_vendors, llm, voice, vectors = self._detect_ai()

        html = self.metric_grid([
            (len(ai_companies), f'AI/ML Companies ({len(ai_companies)/N*100:.0f}%)', theme.PURPLE),
            (llm.get('OpenAI', 0), 'Use OpenAI', theme.GREEN),
            (llm.get('Anthropic', 0), 'Use Anthropic', theme.BLUE),
            (sum(vectors.values()), 'Use Vector DBs', theme.ORANGE),
        ])

        html += self.section('AI/ML in the Portfolio', f"""
<p>{len(ai_companies)} of {N} companies ({len(ai_companies)/N*100:.0f}%) are AI/ML-related based on
product description and vendor analysis.</p>

{self.chart_img('ai_share.png')}
""")

        if (self.output_dir / 'llm_providers.png').exists():
            html += self.section('LLM Provider Landscape', f"""
<p>OpenAI dominates as the LLM provider of choice, but Anthropic and Google are gaining ground.
A small number of companies run self-hosted models (Llama/FIXIE).</p>

{self.chart_img('llm_providers.png')}

{self.insight_box("<strong>Self-hosted LLMs</strong> (Llama, vLLM on Modal/Baseten) represent higher technical complexity but better IP protection and cost control at scale. Companies with self-hosted models tend to have more sophisticated infrastructure.")}
""")

        if (self.output_dir / 'ai_vendors.png').exists():
            html += self.section('AI Vendor Ecosystem', f"""
{self.chart_img('ai_vendors.png')}

<h3>Emerging AI Tech Stack</h3>
{self.table(['Layer', 'Dominant', 'Alternatives'], [
    ['LLM API', 'OpenAI', 'Anthropic, Google Gemini, Perplexity'],
    ['Voice AI', 'ElevenLabs + Twilio', 'Deepgram, AssemblyAI'],
    ['Vector DB', 'Pinecone', 'Weaviate, Qdrant, pgvector'],
    ['ML Inference', 'Modal, Baseten', 'Replicate, SageMaker'],
    ['Auth', 'Clerk, STYTCH', 'Auth0, Okta'],
])}
""")
        return html

if __name__ == "__main__":
    AIMLInfrastructure().run()
