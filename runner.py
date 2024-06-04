from STT import STTAgent

if __name__ == '__main__':
    stt = STTAgent()
    text = stt.run()
    if text is not None:
        print(text)
