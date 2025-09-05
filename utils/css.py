import streamlit as st


class CSSManager:
    """Simple CSS management class"""
    
    def __init__(self):
        self.styles = {
            'main_header': """
                .main-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem; border-radius: 15px; text-align: center;
                    color: white; margin-bottom: 2rem; user-select: none;
                }
            """,
            'feature_card': """
                .feature-card {
                    background: white; padding: 2rem; border-radius: 15px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 1rem 0;
                    border-left: 5px solid #667eea; transition: all .3s;
                }
                .feature-card:hover {
                    transform: translateY(-5px); box-shadow: 0 12px 35px rgba(0,0,0,.15);
                }
            """,
            'buttons': """
                .stButton>button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; border: none; padding: 0.75rem 1.5rem;
                    border-radius: 10px; font-weight: bold; cursor: pointer;
                    transition: all 0.3s ease;
                }
                .stButton>button:hover {
                    transform: translateY(-2px);
                }
            """,
            'containers': """
                .auth-container {
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 3rem; border-radius: 20px;
                }
            """,
            'messages': """
                .success-message {
                    background: #d4edda; color: #155724; padding: 1rem; border-radius: 10px;
                }
                .error-message {
                    background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 10px;
                }
            """,
            'profile': """
                .profile-pic {
                    border-radius: 50%; width: 150px; height: 150px; object-fit: cover;
                    border: 3px solid #667eea; margin-bottom: 1rem;
                }
            """,
            'typography': """
                body { font-family: 'Segoe UI', 'sans-serif'; }
                h1, h2 { color: #4051B5; }
            """
        }
    
    def get_all_styles(self):
        """Get all CSS styles combined"""
        return f"<style>{''.join(self.styles.values())}</style>"
    
    def get_style(self, style_name):
        """Get specific style by name"""
        return f"<style>{self.styles.get(style_name, '')}</style>"
    
    def load_all_styles(self):
        """Load all CSS styles into Streamlit"""
        st.markdown(self.get_all_styles(), unsafe_allow_html=True)
    
    def load_style(self, style_name):
        """Load specific style into Streamlit"""
        st.markdown(self.get_style(style_name), unsafe_allow_html=True)


# Global CSS manager instance
css_manager = CSSManager()


# Keep original function for backward compatibility
def load_css():
    """Load all CSS styles (backward compatible)"""
    css_manager.load_all_styles()


# Additional utility functions
def load_specific_css(style_name):
    """Load specific CSS style"""
    css_manager.load_style(style_name)


def get_css_styles():
    """Get all CSS styles as string"""
    return css_manager.get_all_styles()
