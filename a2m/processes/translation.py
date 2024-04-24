from google.cloud import translate_v2 as translate


def translate_text(text: str):

    translate_client = translate.Client()
    
    target = "ja"
    translation = translate_client.translate(text, target_language=target)
    if 'translatedText' in translation:
        translated_text = translation['translatedText']
        
    return translated_text


if __name__ == "__main__":
    text = """
    This is an introductory chapter on how to calculate nonequilibrium Green's functions via dynamical mean-field theory for the Autumn School on Correlated Electrons: Many-Body Methods for Real Materials, 16-20 September 2019, Forschungszentrum Juelich. It is appropriate for graduate students with a solid state physics and advanced quantum mechanics background.
    """
    print(text)
    print("\n=>\n")
    text_transed = translate_text(text=text)
    print(text_transed)
