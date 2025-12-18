'use client';

import Link from 'next/link';
import { useState, useRef } from 'react';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    topic: 'general',
    message: ''
  });
  const [isRecording, setIsRecording] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle');
  // Web Speech API types not available in TypeScript
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const startDictation = () => {
    // Check if browser supports speech recognition
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
      return;
    }

    if (isRecording) {
      // Stop recording
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    // Start recording
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsRecording(true);
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onresult = (event: any) => {
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        }
      }

      if (finalTranscript) {
        setFormData(prev => ({
          ...prev,
          message: prev.message + finalTranscript
        }));
      }
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitStatus('sending');

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setSubmitStatus('success');
        // Reset form after 3 seconds
        setTimeout(() => {
          setFormData({
            name: '',
            email: '',
            company: '',
            topic: 'general',
            message: ''
          });
          setSubmitStatus('idle');
        }, 3000);
      } else {
        setSubmitStatus('error');
        console.error('Form submission error:', data.error);
        // Reset error state after 3 seconds
        setTimeout(() => {
          setSubmitStatus('idle');
        }, 3000);
      }
    } catch (error) {
      setSubmitStatus('error');
      console.error('Network error:', error);
      // Reset error state after 3 seconds
      setTimeout(() => {
        setSubmitStatus('idle');
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <nav className="border-b border-[var(--border)] py-4">
        <div className="container flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gradient">
            Empathy
          </Link>
          <div className="flex gap-6">
            <Link href="/framework" className="text-sm hover:text-[var(--primary)]">Framework</Link>
            <Link href="/book" className="text-sm hover:text-[var(--primary)]">Book</Link>
            <Link href="/docs" className="text-sm hover:text-[var(--primary)]">Docs</Link>
            <Link href="/plugins" className="text-sm hover:text-[var(--primary)]">Plugins</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-20 gradient-primary text-white">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              Contact Us
            </h1>
            <p className="text-2xl mb-8 opacity-90">
              Questions about the framework? Looking to partner? We&apos;d love to hear from you.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-2xl mx-auto">
            <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Name */}
                <div>
                  <label htmlFor="name" className="block text-sm font-bold mb-2">
                    Name *
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none"
                    placeholder="Your name"
                  />
                </div>

                {/* Email */}
                <div>
                  <label htmlFor="email" className="block text-sm font-bold mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none"
                    placeholder="your.email@example.com"
                  />
                </div>

                {/* Company */}
                <div>
                  <label htmlFor="company" className="block text-sm font-bold mb-2">
                    Company (Optional)
                  </label>
                  <input
                    type="text"
                    id="company"
                    name="company"
                    value={formData.company}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none"
                    placeholder="Your company name"
                  />
                </div>

                {/* Topic */}
                <div>
                  <label htmlFor="topic" className="block text-sm font-bold mb-2">
                    Topic *
                  </label>
                  <select
                    id="topic"
                    name="topic"
                    required
                    value={formData.topic}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none"
                  >
                    <option value="general">General Inquiry</option>
                    <option value="business">Business Partnership</option>
                    <option value="volume">Volume Licensing</option>
                    <option value="technical">Technical Question</option>
                    <option value="healthcare">Healthcare Implementation</option>
                    <option value="anthropic">Anthropic Partnership</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* Message with Dictation */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label htmlFor="message" className="block text-sm font-bold">
                      Message *
                    </label>
                    <button
                      type="button"
                      onClick={startDictation}
                      className={`flex items-center gap-2 px-3 py-1 rounded-lg text-sm font-bold transition-all ${
                        isRecording
                          ? 'bg-[var(--error)] text-white'
                          : 'bg-[var(--accent)] bg-opacity-10 text-[var(--accent)] hover:bg-opacity-20'
                      }`}
                    >
                      {isRecording ? (
                        <>
                          <span className="inline-block w-2 h-2 bg-white rounded-full animate-pulse"></span>
                          Stop Recording
                        </>
                      ) : (
                        <>
                          🎤 Start Dictation
                        </>
                      )}
                    </button>
                  </div>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={6}
                    value={formData.message}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none resize-vertical"
                    placeholder="Tell us about your question, project, or partnership opportunity. You can type or use the dictation button above to speak your message."
                  />
                  <p className="mt-2 text-xs text-[var(--muted)]">
                    💡 Tip: Click &quot;Start Dictation&quot; to use voice input. Works in Chrome and Edge browsers.
                  </p>
                </div>

                {/* Submit Button */}
                <div>
                  <button
                    type="submit"
                    disabled={submitStatus === 'sending' || submitStatus === 'success'}
                    className="w-full btn btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitStatus === 'sending' && 'Sending...'}
                    {submitStatus === 'success' && '✓ Message Sent!'}
                    {submitStatus === 'idle' && 'Send Message'}
                    {submitStatus === 'error' && 'Try Again'}
                  </button>
                </div>

                {submitStatus === 'success' && (
                  <div className="bg-[var(--success)] bg-opacity-10 border-2 border-[var(--success)] rounded-lg p-4 text-center">
                    <p className="text-[var(--success)] font-bold">
                      Thank you! We&apos;ll get back to you within 24-48 hours.
                    </p>
                  </div>
                )}
              </form>
            </div>

            {/* Alternative Contact Methods */}
            <div className="mt-12 grid md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-[var(--border)] bg-opacity-30 rounded-lg">
                <div className="text-3xl mb-3">📧</div>
                <h3 className="font-bold mb-2">Email</h3>
                <a href="mailto:patrick.roebuck@pm.me" className="text-sm text-[var(--accent)] hover:underline">
                  patrick.roebuck@pm.me
                </a>
              </div>

              <div className="text-center p-6 bg-[var(--border)] bg-opacity-30 rounded-lg">
                <div className="text-3xl mb-3">💬</div>
                <h3 className="font-bold mb-2">GitHub Discussions</h3>
                <a href="https://github.com/Smart-AI-Memory/empathy-framework/discussions" className="text-sm text-[var(--accent)] hover:underline" target="_blank" rel="noopener noreferrer">
                  Community Support
                </a>
              </div>

              <div className="text-center p-6 bg-[var(--border)] bg-opacity-30 rounded-lg">
                <div className="text-3xl mb-3">🐛</div>
                <h3 className="font-bold mb-2">Bug Reports</h3>
                <a href="https://github.com/Smart-AI-Memory/empathy-framework/issues" className="text-sm text-[var(--accent)] hover:underline" target="_blank" rel="noopener noreferrer">
                  GitHub Issues
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-[var(--border)]">
        <div className="container">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="text-sm text-[var(--muted)]">
              © 2025 Deep Study AI, LLC. All rights reserved.
            </div>
            <div className="flex gap-6">
              <Link href="/" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Home
              </Link>
              <Link href="/framework" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Framework
              </Link>
              <Link href="/book" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Book
              </Link>
              <Link href="/docs" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Docs
              </Link>
              <Link href="/plugins" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Plugins
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
