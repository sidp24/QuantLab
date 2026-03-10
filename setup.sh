mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
base = \"dark\"\n\
primaryColor = \"#00D4FF\"\n\
backgroundColor = \"#0E1117\"\n\
secondaryBackgroundColor = \"#262730\"\n\
textColor = \"#FAFAFA\"\n\
" > ~/.streamlit/config.toml
