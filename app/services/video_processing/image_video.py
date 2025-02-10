from typing import List, Optional
import os
from moviepy import (
    ImageClip,
    concatenate_videoclips,
)
from loguru import logger
from app.models.material import MaterialInfo, MaterialType

class ImageVideoProcessor:
    def __init__(self):
        self.transition_duration = 1.0  # seconds
        self.clip_duration = 5.0  # seconds per image
        self.zoom_effect = True  # Enable Ken Burns effect
        
    def create_video_from_images(
        self,
        materials: List[MaterialInfo],
        output_path: str,
    ) -> str:
        """Create a base video from a sequence of images with transitions and effects
        
        Args:
            materials: List of MaterialInfo objects containing image paths
            output_path: Path where the video will be saved
        
        Returns:
            Path to the created video file
        """
        try:
            clips = []
            
            for material in materials:
                if material.type != MaterialType.MIDJOURNEY:
                    continue
                    
                # Create image clip with duration
                image_clip = ImageClip(material.url).with_duration(self.clip_duration)
                
                if self.zoom_effect:
                    # Add subtle zoom effect (Ken Burns effect)
                    zoom_factor = 1.1
                    image_clip = image_clip.resized(lambda t: zoom_factor + t/self.clip_duration * 0.1)
                
                # Center the image
                image_clip = image_clip.with_position('center')
                
                # Add to clips list
                clips.append(image_clip)
            
            if not clips:
                raise ValueError("No valid image materials provided")
                
            # Concatenate all clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write video file without audio
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio=False,
                threads=4,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating video from images: {str(e)}")
            raise
        finally:
            # Clean up resources
            if 'final_video' in locals():
                try:
                    final_video.close()
                except:
                    pass
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass
