import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

# --- Funciones ---
def iniciar_sesion(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(random.uniform(3, 6))
    driver.find_element(By.ID, 'username').send_keys(email)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'password').send_keys(Keys.RETURN)
    time.sleep(random.uniform(3, 6))

def buscar_perfiles(driver, keyword):
    busqueda = f'https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER'
    driver.get(busqueda)
    time.sleep(random.uniform(5, 10))
    perfiles = driver.find_elements(By.CSS_SELECTOR, '.entity-result__title-text a')
    resultados = []
    for perfil in perfiles:
        url = perfil.get_attribute('href')
        nombre = perfil.text
        resultados.append({'nombre': nombre, 'url': url})
    return resultados

def enviar_mensaje(driver, perfil_url, nombre, mensaje):
    driver.get(perfil_url)
    time.sleep(random.uniform(5, 10))
    try:
        boton_msg = driver.find_element(By.XPATH, "//button[contains(@class, 'message-anywhere-button')]")
        boton_msg.click()
        time.sleep(random.uniform(2, 4))
        caja_msg = driver.find_element(By.XPATH, "//div[@role='textbox']")
        personalizado = mensaje.replace('[Nombre]', nombre)
        caja_msg.send_keys(personalizado)
        time.sleep(random.uniform(1, 3))
        boton_enviar = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Enviar')]")
        boton_enviar.click()
        time.sleep(random.uniform(2, 4))
        return True
    except Exception as e:
        st.error(f"No se pudo enviar mensaje a {nombre}: {e}")
        return False

# --- App de Streamlit ---
st.title('LinkedIn Messenger Automation')

email = st.text_input('Email de LinkedIn')
password = st.text_input('Contraseña', type='password')
keyword = st.text_input('Palabra clave para buscar perfiles (ej. \"Ingeniero de Datos\")')
mensaje = st.text_area('Mensaje personalizado (usa [Nombre] para personalizar)', "Hola [Nombre], me gustaría conectar contigo para hablar sobre oportunidades de colaboración.")
limite_perfiles = st.number_input('Número máximo de perfiles a contactar', min_value=1, max_value=20, value=5)

if st.button('Iniciar automatización'):
    with st.spinner('Automatizando LinkedIn...'):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        iniciar_sesion(driver, email, password)
        perfiles = buscar_perfiles(driver, keyword)

        contador = 0
        for perfil in perfiles[:limite_perfiles]:
            st.write(f"Enviando mensaje a {perfil['nombre']}...")
            exito = enviar_mensaje(driver, perfil['url'], perfil['nombre'], mensaje)
            if exito:
                st.success(f"Mensaje enviado a {perfil['nombre']}")
                contador += 1
            else:
                st.warning(f"Mensaje NO enviado a {perfil['nombre']}")

        driver.quit()
        st.info(f'Terminó la automatización. Total de mensajes enviados: {contador}')
