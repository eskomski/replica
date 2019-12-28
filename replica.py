from pyo import *
from pyotools import PWM

s = Server()
s.setMidiInputDevice(3)
s.setInOutDevice(8)
s.boot()
s.start()

note = Notein(scale=1)
env = MidiAdsr(note['velocity'] > 0, attack=0.001, decay=1, sustain=1, release=0.001)

# midi cc control objects
# mapped to CC values from AKAI MPK 49
midi_cc = {'attack'   : Midictl(12, 0.001, 3),
           'decay'    : Midictl(13, 0.002, 3),
           'sustain'  : Midictl(14),
           'release'  : Midictl(15, 0.002, 3),
           'lfo_rate' : Midictl(22, 0.3, 20.0, init=0.3),
           'vibrato'  : Midictl(27, 0.0, 4.0),
           'pulsewid' : Port(Midictl(16, 0.5, 1.1, init=0.5), 0.1),
           'sub_osc'  : Midictl(26),
           'noise'    : Midictl(17),
           'filt_cut' : Port(Midictl(18, 100.0, 10000.0, init=10000.0), 0.1),
           'filt_res' : Port(Midictl(19, 0.0, 1.0), 0.1),
           'filt_lfo' : Midictl(28),
           'filt_env' : Midictl(29)}

# lfo
lfo = LFO(freq=midi_cc['lfo_rate'], type=3)
vib = lfo*midi_cc['vibrato']

# oscillators
noise = Noise(mul=env*midi_cc['noise'])
pwm = PWM(note['pitch']+vib, duty=midi_cc['pulsewid'], mul=env, damp=3)
sub = PWM((note['pitch']/2)+vib, duty=0.5, mul=env*midi_cc['sub_osc'], damp=3)
tri = LFO(note['pitch']+vib, mul=env)

# mix down, apply filter
mix = Mix([pwm, tri, sub, noise], mul=0.05, voices=10)
filt = MoogLP(mix, freq=midi_cc['filt_cut'], res=midi_cc['filt_res']).out()

# env parameters don't like PyoObjects, so floats from Midictl objects are retrieved
# when a change is detected
cc_trig = { i : Change(midi_cc[i]) for i in midi_cc.keys() }
t_funcs = [TrigFunc(cc_trig['attack'], lambda: env.setAttack(midi_cc['attack'].get())),
           TrigFunc(cc_trig['decay'], lambda: env.setDecay(midi_cc['decay'].get())),
           TrigFunc(cc_trig['sustain'], lambda: env.setSustain(midi_cc['sustain'].get())),
           TrigFunc(cc_trig['release'], lambda: env.setRelease(midi_cc['release'].get()))]

s.gui(locals())