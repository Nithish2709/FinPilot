import React, { useState } from 'react';
import { X, Lock, Mail, User as UserIcon, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'login') {
        await login({ email, password });
      } else {
        if (!name.trim()) {
          setError('Please provide your name');
          setLoading(false);
          return;
        }
        await register({ name, email, password });
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="w-full max-w-md bg-[#111319] border border-[#00f0ff]/30 rounded-2xl shadow-[0_0_50px_-12px_rgba(0,240,255,0.25)] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-5 bg-gradient-to-r from-[#191c21] via-[#1d2025] to-[#191c21] border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-[#00f0ff]/10 text-[#00f0ff]">
              <Lock className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-['Plus_Jakarta_Sans'] text-base font-bold text-[#dbfcff]">
                {mode === 'login' ? 'Authenticate Session' : 'Create FinPilot Account'}
              </h3>
              <p className="font-['JetBrains_Mono'] text-[11px] text-[#849495]">
                SECURE TOKEN ARCHITECTURE // AES-256
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#849495] hover:text-[#e2e2ea] hover:bg-white/5 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
          {error && (
            <div className="p-3 rounded-xl bg-[#93000a]/20 border border-[#ffb4ab]/40 flex items-start gap-2.5 text-[#ffb4ab] text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {mode === 'register' && (
            <div className="flex flex-col gap-1.5">
              <label className="font-['JetBrains_Mono'] text-xs text-[#b9cacb]">Full Name</label>
              <div className="relative flex items-center">
                <UserIcon className="absolute left-3 w-4 h-4 text-[#849495]" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Siddharth Roy"
                  className="w-full bg-[#191c21] text-[#e2e2ea] placeholder:text-[#849495] text-xs rounded-xl pl-9 pr-4 py-2.5 border border-white/5 focus:border-[#00f0ff]/60 focus:outline-none"
                />
              </div>
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label className="font-['JetBrains_Mono'] text-xs text-[#b9cacb]">Email Address</label>
            <div className="relative flex items-center">
              <Mail className="absolute left-3 w-4 h-4 text-[#849495]" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@finpilot.io"
                className="w-full bg-[#191c21] text-[#e2e2ea] placeholder:text-[#849495] text-xs rounded-xl pl-9 pr-4 py-2.5 border border-white/5 focus:border-[#00f0ff]/60 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="font-['JetBrains_Mono'] text-xs text-[#b9cacb]">Password (min 8 chars)</label>
            <div className="relative flex items-center">
              <Lock className="absolute left-3 w-4 h-4 text-[#849495]" />
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-[#191c21] text-[#e2e2ea] placeholder:text-[#849495] text-xs rounded-xl pl-9 pr-4 py-2.5 border border-white/5 focus:border-[#00f0ff]/60 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 w-full py-2.5 rounded-xl bg-gradient-to-r from-[#0068ed] to-[#00f0ff] hover:opacity-95 text-[#002022] font-['Plus_Jakarta_Sans'] text-xs font-bold flex items-center justify-center gap-2 shadow-[0_0_20px_-4px_rgba(0,240,255,0.4)] disabled:opacity-50 transition-all cursor-pointer"
          >
            {loading ? (
              <span>Authenticating...</span>
            ) : (
              <>
                <span>{mode === 'login' ? 'Establish Session' : 'Create & Login'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>

          {/* Toggle */}
          <div className="pt-3 text-center border-t border-white/5 text-xs text-[#849495]">
            {mode === 'login' ? (
              <span>
                New user?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('register'); setError(null); }}
                  className="text-[#00f0ff] hover:underline font-semibold"
                >
                  Register Account
                </button>
              </span>
            ) : (
              <span>
                Already registered?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('login'); setError(null); }}
                  className="text-[#00f0ff] hover:underline font-semibold"
                >
                  Sign In
                </button>
              </span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};
