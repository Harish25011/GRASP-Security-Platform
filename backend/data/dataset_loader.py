"""CICIDS2017 dataset loader — loads real network traffic data from UNB CSV files."""
import os
import pandas as pd
import numpy as np


class DatasetLoader:
    """Loads CICIDS2017 dataset from GeneratedLabelledFlows CSVs."""

    # Core features used by agents
    FEATURE_COLUMNS = [
        'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
        'Flow Bytes/s', 'Flow Packets/s', 'Fwd Packet Length Mean',
        'Bwd Packet Length Mean', 'Flow IAT Mean', 'Fwd Packet Length Max',
        'Packet Length Mean', 'Packet Length Std', 'Average Packet Size',
        'SYN Flag Count', 'ACK Flag Count', 'PSH Flag Count',
        'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
        'Destination Port', 'Subflow Fwd Bytes', 'Subflow Bwd Bytes',
    ]
    LABEL_COLUMN = 'Label'

    # Dataset paths (prefer GeneratedLabelledFlows for IP addresses)
    DATA_DIRS = [
        'GeneratedLabelledFlows/TrafficLabelling',
        'MachineLearningCSV/MachineLearningCVE',
    ]

    # Map CICIDS2017 labels to attack categories
    LABEL_MAP = {
        'BENIGN': 'benign',
        'DDoS': 'ddos',
        'PortScan': 'port_scan',
        'Bot': 'c2_beacon',
        'Infiltration': 'lateral_movement',
        'Web Attack \x96 Brute Force': 'brute_force',
        'Web Attack \x96 XSS': 'xss',
        'Web Attack \x96 Sql Injection': 'sql_injection',
        'Web Attack Brute Force': 'brute_force',
        'Web Attack XSS': 'xss',
        'Web Attack Sql Injection': 'sql_injection',
        'FTP-Patator': 'brute_force',
        'SSH-Patator': 'brute_force',
        'DoS Hulk': 'ddos',
        'DoS GoldenEye': 'ddos',
        'DoS slowloris': 'ddos',
        'DoS Slowhttptest': 'ddos',
        'Heartbleed': 'zero_day',
    }

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.dirname(__file__)
        self.data = None
        self._stats = {}

    def _find_csv_dir(self):
        """Find the best directory with CSV files."""
        for subdir in self.DATA_DIRS:
            full_path = os.path.join(self.data_dir, subdir)
            if os.path.isdir(full_path):
                csvs = [f for f in os.listdir(full_path) if f.endswith('.csv')]
                if csvs:
                    return full_path, csvs
        # Fallback: look in data_dir itself
        csvs = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        if csvs:
            return self.data_dir, csvs
        return None, []

    def load(self, filename=None, sample_size=5000) -> pd.DataFrame:
        """Load dataset. Samples from all CSVs for memory efficiency.

        Args:
            filename: Specific CSV file to load (optional).
            sample_size: Number of rows to sample from each CSV (default 5000).
        """
        csv_dir, csv_files = self._find_csv_dir()

        if filename:
            return self._load_single(os.path.join(self.data_dir, filename))

        if not csv_dir or not csv_files:
            print("[DataLoader] No CSV files found, generating sample data")
            return self._generate_sample_data()

        print(f"[DataLoader] Found {len(csv_files)} CICIDS2017 CSV files in {csv_dir}")
        frames = []
        per_file = max(500, sample_size // len(csv_files))

        for csv_file in sorted(csv_files):
            filepath = os.path.join(csv_dir, csv_file)
            try:
                # Try multiple encodings (CICIDS2017 uses special chars in labels)
                for enc in ['utf-8', 'cp1252', 'latin-1']:
                    try:
                        df = pd.read_csv(filepath, encoding=enc, low_memory=False)
                        break
                    except UnicodeDecodeError:
                        continue
                df.columns = df.columns.str.strip()

                # Clean data
                df = df.replace([np.inf, -np.inf], np.nan)
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].fillna(0)

                # Normalize labels
                if 'Label' in df.columns:
                    df['Label'] = df['Label'].str.strip()

                # Stratified sample: keep attack ratios realistic
                if len(df) > per_file:
                    attacks = df[df['Label'] != 'BENIGN']
                    benign = df[df['Label'] == 'BENIGN']
                    n_attacks = min(len(attacks), per_file // 3)
                    n_benign = min(len(benign), per_file - n_attacks)
                    sampled = pd.concat([
                        attacks.sample(n=n_attacks, random_state=42) if n_attacks > 0 else attacks,
                        benign.sample(n=n_benign, random_state=42),
                    ])
                    frames.append(sampled)
                else:
                    frames.append(df)

                day = csv_file.split('-')[0]
                n_attacks_in_file = len(df[df['Label'] != 'BENIGN'])
                print(f"  [OK] {csv_file[:40]:<40} {len(df):>8} rows | {n_attacks_in_file:>6} attacks")

            except Exception as e:
                print(f"  [FAIL] Error loading {csv_file}: {e}")

        if not frames:
            return self._generate_sample_data()

        self.data = pd.concat(frames, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

        # Compute stats
        total = len(self.data)
        labels = self.data['Label'].value_counts()
        self._stats = {
            'total_rows': total,
            'attack_rows': int((self.data['Label'] != 'BENIGN').sum()),
            'benign_rows': int((self.data['Label'] == 'BENIGN').sum()),
            'attack_types': {k: int(v) for k, v in labels.items() if k != 'BENIGN'},
            'unique_sources': int(self.data['Source IP'].nunique()) if 'Source IP' in self.data.columns else 0,
            'unique_destinations': int(self.data['Destination IP'].nunique()) if 'Destination IP' in self.data.columns else 0,
        }
        print(f"[DataLoader] Loaded {total} rows | {self._stats['attack_rows']} attacks | {self._stats['unique_sources']} unique sources")
        return self.data

    def _load_single(self, filepath) -> pd.DataFrame:
        try:
            df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
            df.columns = df.columns.str.strip()
            df = df.replace([np.inf, -np.inf], np.nan).dropna()
            self.data = df
            return df
        except Exception as e:
            print(f"[DataLoader] Error loading {filepath}: {e}")
            return self._generate_sample_data()

    def _generate_sample_data(self) -> pd.DataFrame:
        """Fallback: generate sample data for development."""
        n = 500
        data = {
            'Source IP': [f"192.168.1.{np.random.randint(10, 50)}" for _ in range(n)],
            'Destination IP': [f"10.0.0.{np.random.randint(1, 30)}" for _ in range(n)],
            'Protocol': np.random.choice([6, 17, 0], n),  # TCP=6, UDP=17
            'Destination Port': np.random.choice([80, 443, 22, 21, 8080, 3389], n),
            'Flow Duration': np.random.exponential(1000, n),
            'Total Fwd Packets': np.random.poisson(10, n),
            'Total Backward Packets': np.random.poisson(8, n),
            'Flow Bytes/s': np.random.exponential(5000, n),
            'Flow Packets/s': np.random.exponential(50, n),
            'Fwd Packet Length Mean': np.random.exponential(200, n),
            'Bwd Packet Length Mean': np.random.exponential(150, n),
            'Flow IAT Mean': np.random.exponential(100, n),
            'Label': np.random.choice(
                ['BENIGN', 'DDoS', 'PortScan', 'Bot', 'Infiltration', 'Web Attack Brute Force'],
                n, p=[0.7, 0.08, 0.06, 0.06, 0.05, 0.05]
            ),
        }
        self.data = pd.DataFrame(data)
        print("[DataLoader] Using generated sample data (no CSV found)")
        return self.data

    def to_events(self) -> list:
        """Convert dataframe rows to event dicts for graph building."""
        if self.data is None:
            self.load()

        events = []
        for _, row in self.data.iterrows():
            label_raw = str(row.get('Label', 'BENIGN')).strip()
            label = self.LABEL_MAP.get(label_raw, label_raw.lower().replace(' ', '_'))
            protocol_num = row.get('Protocol', 6)
            protocol_map = {6: 'TCP', 17: 'UDP', 0: 'HOPOPT', 1: 'ICMP'}

            events.append({
                "source_ip": str(row.get('Source IP', f'192.168.1.{np.random.randint(10,50)}')),
                "dest_ip": str(row.get('Destination IP', f'10.0.0.{np.random.randint(1,30)}')),
                "dest_port": int(row.get('Destination Port', 0)),
                "protocol": protocol_map.get(int(protocol_num), str(protocol_num)) if pd.notna(protocol_num) else 'TCP',
                "flow_duration": float(row.get('Flow Duration', 0)),
                "bytes_sent": float(row.get('Flow Bytes/s', 0)),
                "bytes_recv": float(row.get('Bwd Packet Length Mean', 0)),
                "fwd_packets": int(row.get('Total Fwd Packets', 0)),
                "bwd_packets": int(row.get('Total Backward Packets', 0)),
                "packet_length_mean": float(row.get('Packet Length Mean', 0)) if 'Packet Length Mean' in row.index else 0,
                "label": label,
                "label_raw": label_raw,
            })
        return events

    def get_stats(self) -> dict:
        """Return dataset statistics."""
        return self._stats
