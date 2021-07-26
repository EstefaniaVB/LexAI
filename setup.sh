mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[theme]\n\
base='light'\n\
primaryColor='#6082fd'\n\
secondaryBackgroundColor='#f7f7f7'\n\
textColor='#000000'\n\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml