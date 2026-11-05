import sherpa_onnx, soundfile as sf, sys, time
d="/tmp/tts/sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(tokens=d+"tokens.txt",encoder=d+"encoder.int8.onnx",decoder=d+"decoder.int8.onnx",vocoder="/tmp/tts/vocos.onnx",data_dir=d+"espeak-ng-data",lexicon=d+"lexicon.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg)
PT="那天，主播在食堂吃饭，不小心把汤洒在裤子上了，主播特别尴尬，但又不能直接离开，只能用纸巾擦了又擦。更糟的是，主播的粉丝刚好在旁边还非要过来打招呼，主播只能假装若无其事地聊天，但其实心里慌得要命。"
w,sr=sf.read("/tmp/tts/ref16.wav",dtype="float32")
def gen(t,speed=1.0):
    return tts.generate(t,PT,w.tolist(),sr,speed=speed,num_steps=4)
if __name__=="__main__":
    t0=time.time(); a=gen(sys.argv[1]); sf.write(sys.argv[2],a.samples,a.sample_rate); print(len(a.samples)/a.sample_rate,"s audio in",round(time.time()-t0,1),"s")
