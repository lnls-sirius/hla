"""RaBPM monitor utilities."""

SEC_2_SLOT = {
    'IA': (
        ('Timing', 'EVR'),
        ('FOFB', 'Controller'),
        ('', ''),
        ('Photon BPM', 'S(A|B|P)FE-1'),
        ('Photon BPM', 'S(A|B|P)FE-2'),
        ('Photon BPM', 'BCFE-1'),
        ('Photon BPM', 'BCFE-2'),
        ('ID BPM', 'S(A|B|P)FE-1'),
        ('ID BPM', 'S(A|B|P)FE-2'),
        ('SI BPM', 'M1'),
        ('SI BPM', 'M2'),
        ('SI BPM', 'C1-1'),
        ('SI BPM', 'C1-2'),
        ('SI BPM', 'C2'),
        ('SI BPM', 'C3-1'),
        ('SI BPM', 'C3-2'),
        ('SI BPM', 'C4'),
        ('BO BPM', '[N]U'),
        ('BO BPM', '[N+1]U'),
        ('BO BPM', '[N+2]U'),
        None,
    ),
    'TL': (
        ('Timing', 'EVR'),
        None,
        None,
        None,
        None,
        None,
        None,
        ('TB BPM', '01-1'),
        ('TB BPM', '01-2'),
        ('TB BPM', '02-1'),
        ('TB BPM', '02-2'),
        ('TB BPM', '03'),
        ('TB BPM', '04'),
        ('TS BPM', '01'),
        ('TS BPM', '02'),
        ('TS BPM', '03'),
        ('TS BPM', '04-1'),
        ('TS BPM', '04-2'),
        None,
        None,
        None,
    ),
}