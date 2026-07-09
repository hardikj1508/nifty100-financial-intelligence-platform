from src.analytics.peer import PeerEngine

engine = PeerEngine()

engine.create_peer_percentiles_table()

engine.process_all_peer_groups()

