# whisperx_core/whisperx_configurator.py
class WhisperXConfigurator:

    DEFAULTS = {
        "whisper_model": "large-v2",
        "beam_size": 5,
        "compute_type": "float16",
        "vad_onset": 0.5,
        "vad_offset": 0.363,
        "vad_min_duration_on": 0,
        "vad_min_duration_off": 0,
        "seg_stich_threshold": 0.1,
        "Clustering_threshold": 0.715,
        "clustering_min_cluster_size": 15,
        "embedding_exclude_overlap": True,
        "max_num_speakers": 2,
        "embedding_batch_size": 32,
        "segmentation_batch_size": 32
    }

    def configure(self, params: dict):

        config = self.DEFAULTS.copy()

        for k, v in params.items():
            if v is not None:
                config[k] = v

        return config
