// Hai chế độ mic: WAV cho Google Cloud hoặc nhận diện tiếng Việt của trình duyệt.
// Quyền micro chỉ được xin sau khi người dùng bấm nút. Không tự gửi transcript.
export function wav(samples, sourceRate) {
  const targetRate = 16000;
  const count = Math.floor(samples.length * targetRate / sourceRate);
  const bytes = new ArrayBuffer(44 + count * 2);
  const view = new DataView(bytes);
  const ascii = (at, text) => [...text].forEach((character, index) => view.setUint8(at + index, character.charCodeAt(0)));
  ascii(0, 'RIFF'); view.setUint32(4, bytes.byteLength - 8, true); ascii(8, 'WAVE');
  ascii(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, 1, true); view.setUint32(24, targetRate, true);
  view.setUint32(28, targetRate * 2, true); view.setUint16(32, 2, true);
  view.setUint16(34, 16, true); ascii(36, 'data'); view.setUint32(40, count * 2, true);
  for (let index = 0; index < count; index++) {
    const start = Math.floor(index * sourceRate / targetRate);
    const end = Math.max(start + 1, Math.floor((index + 1) * sourceRate / targetRate));
    let sum = 0;
    for (let sample = start; sample < end && sample < samples.length; sample++) sum += samples[sample];
    const value = Math.max(-1, Math.min(1, sum / (end - start)));
    view.setInt16(44 + index * 2, value < 0 ? Math.round(value * 32768) : Math.round(value * 32767), true);
  }
  return new Blob([bytes], {type:'audio/wav'});
}

export class GoogleMic {
  constructor({onStart, onStatus, onComplete, onEmpty, onError}) {
    Object.assign(this, {onStart, onStatus, onComplete, onEmpty, onError});
    this.active = false; this.buffers = []; this.heardSpeech = false;
  }
  async start() {
    if (!navigator.mediaDevices?.getUserMedia || !window.AudioContext) throw new Error('Trình duyệt cần localhost hoặc HTTPS và quyền micro.');
    this.active = true;
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true, noiseSuppression:true}, video:false});
      if (!this.active) { this.stream.getTracks().forEach(track => track.stop()); return; }
      this.context = new AudioContext();
      this.source = this.context.createMediaStreamSource(this.stream);
      this.processor = this.context.createScriptProcessor(4096, 1, 1);
      this.silent = this.context.createGain(); this.silent.gain.value = 0;
      this.source.connect(this.processor); this.processor.connect(this.silent); this.silent.connect(this.context.destination);
      this.startedAt = Date.now(); this.lastSpeech = this.startedAt;
      this.processor.onaudioprocess = event => {
        if (!this.active) return;
        const samples = new Float32Array(event.inputBuffer.getChannelData(0));
        this.buffers.push(samples);
        let energy = 0;
        for (const sample of samples) energy += sample * sample;
        const now = Date.now();
        if (Math.sqrt(energy / samples.length) >= 0.018) {
          this.heardSpeech = true; this.lastSpeech = now;
        }
        if ((this.heardSpeech && now - this.lastSpeech >= 3000) || now - this.startedAt >= 55000 || (!this.heardSpeech && now - this.startedAt >= 12000)) this.stop(false);
      };
      this.onStart?.();
      this.onStatus?.('Đang nghe… Mic tự dừng sau 3 giây im lặng.');
    } catch (error) { this.stop(true); this.onError?.(error); }
  }
  stop(cancel = false) {
    if (!this.active) return;
    this.active = false;
    if (this.processor) this.processor.onaudioprocess = null;
    for (const item of [this.source, this.processor, this.silent]) item?.disconnect();
    this.stream?.getTracks().forEach(track => track.stop());
    this.context?.close().catch(() => {});
    if (cancel) return;
    if (!this.heardSpeech) { this.onEmpty?.(); return; }
    const length = this.buffers.reduce((total, buffer) => total + buffer.length, 0);
    const samples = new Float32Array(length);
    let offset = 0;
    for (const buffer of this.buffers) { samples.set(buffer, offset); offset += buffer.length; }
    this.onComplete?.(wav(samples, this.context.sampleRate));
  }
}

export class BrowserMic {
  constructor({onStart, onStatus, onComplete, onEmpty, onError}) {
    Object.assign(this, {onStart, onStatus, onComplete, onEmpty, onError});
    this.active = false;
  }
  start() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition || !window.isSecureContext) throw new Error('Mic trình duyệt cần Chrome trên localhost hoặc HTTPS.');
    this.active = true; this.recognition = new Recognition();
    this.recognition.lang = 'vi-VN'; this.recognition.continuous = true; this.recognition.interimResults = true;
    this.transcript = '';
    this.recognition.onstart = () => { if (this.active) { this.onStart?.(); this.onStatus?.('Đang nghe tiếng Việt… Tự dừng sau 3 giây im lặng.'); } };
    this.recognition.onresult = event => {
      if (!this.active) return;
      this.transcript = Array.from(event.results).map(item => item[0]?.transcript || '').join(' ').trim();
      clearTimeout(this.silenceTimer);
      if (this.transcript) this.silenceTimer = setTimeout(() => this.stop(false), 3000);
    };
    this.recognition.onerror = event => {
      if (!this.active) return;
      const message = event.error === 'not-allowed' ? 'Bạn chưa cho phép dùng micro.' : 'Mic trình duyệt chưa nhận diện được. Bạn thử lại hoặc gõ câu hỏi.';
      this.stop(true); this.onError?.(new Error(message));
    };
    this.recognition.onend = () => { if (this.active) this.stop(false); };
    this.maxTimer = setTimeout(() => this.stop(false), 55000);
    try { this.recognition.start(); } catch (error) { this.stop(true); throw error; }
  }
  stop(cancel = false) {
    if (!this.active) return;
    this.active = false; clearTimeout(this.silenceTimer); clearTimeout(this.maxTimer);
    try { if (cancel) this.recognition?.abort(); else this.recognition?.stop(); } catch { /* Đã dừng. */ }
    if (cancel) return;
    if (this.transcript) this.onComplete?.(this.transcript);
    else this.onEmpty?.();
  }
}
