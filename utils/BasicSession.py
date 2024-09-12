import streamlit as st
from langchain_core.messages import AIMessage, SystemMessage

class BasicSession():
    
    def session_init(self) -> None:
        defaultContext = "Vous êtes mon assistant pluridisciplinaire et vous m'aidez dans des tâches d'analyse documentaire."
        self.session_register("opt_system_context",default=defaultContext)
        self.session_register("history",default=self.history_new())
        self.session_register("opt_debug",default=False)
        self.session_register("opt_kfragments",default=3)
        self.session_register("selected_docs",default=[])
        
        self.session_register("llm_modelname","groq") # init port, set to zero ! nor 1573
        self.session_register("llm_port","groq") # init port, set to zero ! nor 1573
        
    def no_llm_warn(self):
        if st.session_state.llm_modelname =="" or st.session_state.llm_port == 0 : 
            st.warning(f"""Aucun modèle n'est sélectionné, rendez-vous sur la page home/modèles. 
                       No running model on port : {st.session_state.llm_port}""")
            
    def session_register(self,name,default):
        if name not in st.session_state:
            st.session_state[name]= default
            
    def session_show(self):
        msg=""
        for key in st.session_state.keys():
            val = st.session_state[key]
            msg += f"\n{key} : {val}" 
        st.toast(msg)
            
    def session_kill(self):
        for key in st.session_state.keys():
            val = st.session_state[key]
            del st.session_state[key]
    def history_reset(self):
        st.session_state.history = self.history_new()
        
    def history_new(self):
        resetRag = [
            SystemMessage(content=st.session_state.opt_system_context),
            AIMessage(content="Bonjour, comment puis-je vous aider?"),
        ]
        return resetRag
    
