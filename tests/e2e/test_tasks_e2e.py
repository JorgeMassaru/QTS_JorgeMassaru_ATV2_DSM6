from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Configura e retorna o driver do Chrome."""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver


def test_add_note_appears_in_list_e2e():
    """
    E2E: Adicionar uma nota pelo formulário e verificar
    que ela aparece na lista da página.
    """
    driver = setup_driver()

    try:
        driver.get("http://127.0.0.1:5000")

        title_input = driver.find_element(By.ID, "title")
        title_input.send_keys("Nota E2E Teste")

        driver.find_element(By.ID, "submit").click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "note-list"),
                "Nota E2E Teste",
            )
        )

        assert "Nota E2E Teste" in driver.page_source

    finally:
        driver.quit()


def test_add_multiple_notes_e2e():
    """
    E2E: Adicionar duas notas e verificar que ambas aparecem na lista.
    """
    driver = setup_driver()

    try:
        driver.get("http://127.0.0.1:5000")

        # Primeira nota
        driver.find_element(By.ID, "title").send_keys("Nota Alpha")
        driver.find_element(By.ID, "submit").click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "note-list"), "Nota Alpha")
        )

        # Segunda nota
        driver.find_element(By.ID, "title").send_keys("Nota Beta")
        driver.find_element(By.ID, "submit").click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "note-list"), "Nota Beta")
        )

        assert "Nota Alpha" in driver.page_source
        assert "Nota Beta" in driver.page_source

    finally:
        driver.quit()


# ── 2 novos testes E2E ────────────────────────────────────────────────────────


def test_page_title_is_correct_e2e():
    """
    E2E: Verifica que o título da página é 'Gerenciador de Notas'.
    Garante que o HTML correto é servido pela aplicação.
    """
    driver = setup_driver()

    try:
        driver.get("http://127.0.0.1:5000")

        assert driver.title == "Gerenciador de Notas"

    finally:
        driver.quit()


def test_submit_button_is_present_e2e():
    """
    E2E: Verifica que o botão de adicionar nota existe e está visível.
    Teste de sanidade da interface antes de qualquer interação.
    """
    driver = setup_driver()

    try:
        driver.get("http://127.0.0.1:5000")

        button = driver.find_element(By.ID, "submit")

        assert button.is_displayed()
        assert button.text == "Adicionar Nota"

    finally:
        driver.quit()