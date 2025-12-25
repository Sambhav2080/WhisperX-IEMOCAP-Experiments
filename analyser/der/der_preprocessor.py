from pyannote.core import Annotation, Segment


class DERPreprocessor:
    """
    Cleans diarization annotations before DER calculation.
    """

    def __init__(self,
                 min_duration=0.05,
                 merge_gap=0.5):
        """
        min_duration : drop segments shorter than this
        merge_gap    : merge same-speaker segments separated by <= gap
        """

        self.min_duration = min_duration
        self.merge_gap = merge_gap


    def remove_bad_segments(self, ann: Annotation) -> Annotation:
        """
        Remove zero-length and super-tiny segments
        """

        cleaned = Annotation(uri=ann.uri)

        for segment, _, label in ann.itertracks(yield_label=True):

            duration = segment.end - segment.start

            if duration <= 0:
                continue

            if duration < self.min_duration:
                continue

            cleaned[segment] = label

        return cleaned


    def merge_same_speaker(self, ann: Annotation) -> Annotation:
        """
        Merge adjacent same-speaker segments
        if gap <= self.merge_gap
        """

        merged = Annotation(uri=ann.uri)

        # sort by time
        tracks = sorted(
            ann.itertracks(yield_label=True),
            key=lambda x: x[0].start
        )

        if not tracks:
            return merged

        # take first segment
        current_seg, _, current_label = tracks[0]
        start = current_seg.start
        end = current_seg.end

        for segment, _, label in tracks[1:]:

            gap = segment.start - end

            # same speaker + continuous speech
            if label == current_label and gap <= self.merge_gap:
                end = max(end, segment.end)

            else:
                # finalize previous
                merged[Segment(start, end)] = current_label

                # reset
                current_label = label
                start = segment.start
                end = segment.end

        # last segment
        merged[Segment(start, end)] = current_label

        return merged


    def clean(self, ann: Annotation) -> Annotation:
        """
        Full preprocessing pipeline
        """

        ann = self.remove_bad_segments(ann)

        ann = self.merge_same_speaker(ann)

        return ann
