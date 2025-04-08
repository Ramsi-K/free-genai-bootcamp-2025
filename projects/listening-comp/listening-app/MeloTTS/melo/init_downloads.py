if __name__ == "__main__":

    from melo.api import TTS

    device = "auto"
    # Only download the Korean model
    models = {
        "KR": TTS(language="KR", device=device),
    }
