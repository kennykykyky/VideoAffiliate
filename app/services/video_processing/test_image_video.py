import os
import asyncio
from loguru import logger
from app.models.material import MaterialType, MaterialInfo
from app.models.schema import VideoParams, VideoAspect
from app.services.material import MaterialService
from app.services.video_processing.image_video import ImageVideoProcessor
from app.services import voice, subtitle, video, task
from app.utils import utils
import uuid

async def test_basic_image_video():
    """Test the basic image-to-video functionality without audio/subtitles"""
    # Test script with multiple sentences
    test_script = """A majestic lion roaming through the African savanna.
A group of elephants drinking at a waterhole under the sunset.
A flock of colorful birds flying across a rainforest canopy.
A cheetah sprinting across the grasslands chasing its prey."""

    try:
        # Initialize services
        material_service = MaterialService()
        video_processor = ImageVideoProcessor()
        
        # Create output directories
        os.makedirs("tests/materials", exist_ok=True)
        os.makedirs("tests/output", exist_ok=True)
        
        print("\nGenerating images from script...")
        materials = await material_service.generate_materials_from_script(
            script=test_script,
            material_type=MaterialType.MIDJOURNEY,
            output_dir="tests/materials"
        )
        
        if not materials:
            raise ValueError("No materials generated")
        
        print(f"\nGenerated {len(materials)} images")
        for i, material in enumerate(materials):
            print(f"\nImage {i+1}:")
            print(f"Sentence: {material.sentence}")
            print(f"Prompt: {material.prompt}")
            print(f"Path: {material.url}")
        
        # Create basic video from images
        output_path = "tests/output/basic_test_video.mp4"
        video_path = video_processor.create_video_from_images(
            materials=materials,
            output_path=output_path
        )
        
        print(f"\nBasic video created successfully: {video_path}")
        
    except Exception as e:
        logger.error(f"Error during basic testing: {str(e)}")
        print(f"\nError: {str(e)}")

async def test_complete_workflow():
    """Test the complete workflow including narration and subtitles"""
    # Test script with multiple sentences
    test_script = """A majestic lion roaming through the African savanna.
A group of elephants drinking at a waterhole under the sunset.
A flock of colorful birds flying across a rainforest canopy.
A cheetah sprinting across the grasslands chasing its prey."""

    try:
        # Initialize video processor
        video_processor = ImageVideoProcessor()
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        task_dir = utils.task_dir(task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # Create test video parameters
        params = VideoParams(
            video_subject="Wildlife in Africa",
            video_script=test_script,
            video_aspect=VideoAspect.landscape,
            voice_name="en-US-JennyNeural",  # Example voice
            voice_rate=1.0,
            voice_volume=1.0,
            subtitle_enabled=True,
            font_name="Arial",
            font_size=48,
            text_fore_color="white",
            stroke_color="black",
            stroke_width=2,
            subtitle_position="bottom"
        )
        
        # Use existing images from tests/materials
        materials = []
        test_materials_dir = "tests/materials"
        for i in range(4):  # We know we have 4 images
            image_path = os.path.join(test_materials_dir, f"image_{i}.png")
            if os.path.exists(image_path):
                materials.append(MaterialInfo(
                    type=MaterialType.MIDJOURNEY,
                    url=image_path,
                    sentence=test_script.split('\n')[i].strip()
                ))
        
        if not materials:
            raise ValueError("No existing materials found in tests/materials directory")
        
        print(f"\nFound {len(materials)} existing images")
        
        # Step 1: Create base video from images
        print("\nCreating base video from images...")
        base_video_path = os.path.join(task_dir, "base_video.mp4")
        video_processor.create_video_from_images(
            materials=materials,
            output_path=base_video_path
        )
        
        # Step 2: Generate audio narration
        print("\nGenerating audio narration...")
        audio_path = os.path.join(task_dir, "audio.mp3")
        sub_maker = voice.tts(
            text=test_script,
            voice_name=voice.parse_voice_name(params.voice_name),
            voice_rate=params.voice_rate,
            voice_file=audio_path
        )
        
        if not sub_maker:
            raise ValueError("Failed to generate audio narration")
        
        # Step 3: Generate subtitles
        print("\nGenerating subtitles...")
        subtitle_path = os.path.join(task_dir, "subtitle.srt")
        subtitle_provider = "whisper"  # For testing, use whisper directly
        subtitle.create(audio_file=audio_path, subtitle_file=subtitle_path)
        subtitle.correct(subtitle_file=subtitle_path, video_script=test_script)
        
        # Step 4: Generate final video with everything combined
        print("\nGenerating final video...")
        final_video_path = os.path.join(task_dir, "final_video.mp4")
        video.generate_video(
            video_path=base_video_path,
            audio_path=audio_path,
            subtitle_path=subtitle_path,
            output_file=final_video_path,
            params=params
        )
        
        print(f"\nComplete video created successfully!")
        print(f"Final video: {final_video_path}")
        print(f"Audio file: {audio_path}")
        print(f"Subtitle file: {subtitle_path}")
        
    except Exception as e:
        logger.error(f"Error during complete workflow testing: {str(e)}")
        print(f"\nError: {str(e)}")

async def test_image_to_video_workflow():
    """Test the complete workflow using local images instead of downloaded videos"""
    # Test script with multiple sentences
    test_script = """A majestic lion roaming through the African savanna.
A group of elephants drinking at a waterhole under the sunset.
A flock of colorful birds flying across a rainforest canopy.
A cheetah sprinting across the grasslands chasing its prey."""

    try:
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        task_dir = utils.task_dir(task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # Create test video parameters
        params = VideoParams(
            video_subject="Wildlife in Africa",
            video_script=test_script,
            video_aspect=VideoAspect.landscape,
            voice_name="en-US-JennyNeural",
            voice_rate=1.0,
            voice_volume=1.0,
            subtitle_enabled=True,
            font_name="Arial",
            font_size=48,
            text_fore_color="white",
            stroke_color="black",
            stroke_width=2,
            subtitle_position="bottom",
            video_source="local",  # Set to use local files
            local_files=[  # Add paths to your test images
                "tests/materials/image_0.png",
                "tests/materials/image_1.png",
                "tests/materials/image_2.png",
                "tests/materials/image_3.png"
            ],
            video_clip_duration=5  # Duration for each image clip
        )
        
        print("\nStarting image-to-video test workflow...")
        
        # Use the task service to run the complete pipeline
        result = task.start(
            task_id=task_id,
            params=params,
            stop_at="video"  # Run the complete pipeline
        )
        
        if result and "videos" in result:
            print("\nTest completed successfully!")
            print(f"Task directory: {task_dir}")
            print(f"Final videos: {result['videos']}")
            print(f"Audio file: {result['audio_file']}")
            if result.get('subtitle_path'):
                print(f"Subtitle file: {result['subtitle_path']}")
        else:
            print("\nTest failed - no videos generated")
            
    except Exception as e:
        logger.error(f"Error during image-to-video testing: {str(e)}")
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("\n=== Image to Video Test ===")
    asyncio.run(test_image_to_video_workflow())
    print("\nTest completed.") 