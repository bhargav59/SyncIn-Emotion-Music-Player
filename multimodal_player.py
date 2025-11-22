"""
Main Multimodal Emotion-Based Music Player
Integrates all components
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.emotion_detection.facial_emotion import FacialEmotionDetector
from src.emotion_detection.audio_emotion import AudioEmotionDetector
from src.emotion_detection.text_emotion import TextEmotionDetector
from src.fusion.multimodal_fusion import MultimodalFusion
from src.music_analysis.music_emotion_recognition import MusicEmotionAnalyzer
from src.recommendation.recommendation_engine import MusicRecommendationEngine
import pygame
import time

class MultimodalMusicPlayer:
    def __init__(self):
        print("🎵 Initializing Multimodal Music Player...")
        
        # Initialize all detectors
        self.facial_detector = FacialEmotionDetector()
        self.audio_detector = AudioEmotionDetector()
        self.text_detector = TextEmotionDetector()
        
        # Initialize fusion
        self.fusion = MultimodalFusion(fusion_method='attention')
        
        # Initialize music analyzer
        self.music_analyzer = MusicEmotionAnalyzer()
        
        # Initialize recommendation engine
        self.recommender = MusicRecommendationEngine(self.music_analyzer)
        
        # Initialize pygame for music
        pygame.mixer.init()
        
        print("✅ All systems ready!\n")
        
    def detect_emotions(self, use_facial=True, use_audio=True, use_text=True):
        """Detect emotions from all available modalities"""
        facial_probs = None
        audio_probs = None
        text_probs = None
        
        print("\n" + "="*60)
        print("🎭 MULTIMODAL EMOTION DETECTION")
        print("="*60)
        
        # Facial emotion detection
        if use_facial:
            print("\n📹 Starting facial emotion detection...")
            print("   Look at the camera. Press ESC to finish.")
            emotion_code = self.facial_detector.detect_from_webcam(num_predictions=10)
            
            # Convert to probabilities
            facial_probs = {
                'angry': 0.9 if emotion_code == '1' else 0.05,
                'happy': 0.9 if emotion_code == '2' else 0.05,
                'neutral': 0.8 if emotion_code == '3' else 0.1,
                'sad': 0.1
            }
            print(f"   ✓ Facial: {max(facial_probs, key=facial_probs.get)}")
            
        # Audio emotion detection
        if use_audio:
            try:
                print("\n🎤 Starting audio emotion detection...")
                emotion, audio_probs = self.audio_detector.detect_from_microphone()
                print(f"   ✓ Audio: {emotion}")
            except Exception as e:
                print(f"   ⚠️  Audio detection skipped: {e}")
                audio_probs = None
                
        # Text emotion detection
        if use_text:
            print("\n💬 Text emotion analysis:")
            print("   (Press Enter to skip)")
            text_input = input("   Your text: ").strip()
            if text_input:
                emotion, text_probs = self.text_detector.detect_from_input(text_input)
                print(f"   ✓ Text: {emotion}")
            else:
                print("   ⊗ Text detection skipped")
                text_probs = None
                
        return facial_probs, audio_probs, text_probs
        
    def fuse_and_recommend(self, facial_probs, audio_probs, text_probs):
        """Fuse emotions and recommend music"""
        # Fuse emotions
        fused_probs = self.fusion.fuse_emotions(facial_probs, audio_probs, text_probs)
        
        # Display results
        detected_emotion = self.fusion.print_fusion_results(fused_probs)
        
        # Get recommendation
        print("\n" + "="*60)
        print("🎯 MUSIC RECOMMENDATION")
        print("="*60)
        
        explanation = self.recommender.get_recommendation_explanation(detected_emotion)
        print(f"\n{explanation}")
        
        song = self.recommender.recommend_song(detected_emotion)
        
        return detected_emotion, song
        
    def play_music(self, song_name, detected_emotion):
        """Play the recommended song"""
        if not song_name:
            print("⚠️  No song available")
            return
            
        song_path = f'songs/{song_name}.mp3'
        
        if not os.path.exists(song_path):
            print(f"⚠️  Song file not found: {song_path}")
            return
            
        try:
            pygame.mixer.music.load(song_path)
            print(f"\n🎵 Now Playing: {song_name}")
            print("\n" + "="*60)
            print("Controls: P=Pause, R=Resume, S=Stop, Q=Quit")
            print("="*60 + "\n")
            
            pygame.mixer.music.play()
            
            # Create simple control window
            screen = pygame.display.set_mode((600, 400))
            pygame.display.set_caption(f"SyncIn Player - {detected_emotion.title()}")
            clock = pygame.time.Clock()
            font = pygame.font.Font(None, 36)
            emoji_font = pygame.font.SysFont("segoeuiemoji", 100) # Try to use a font that supports emojis
            
            # Emoji mapping
            emoji_dict = {
                'angry': '😠', 
                'happy': '😊', 
                'neutral': '😐', 
                'sad': '😢'
            }
            emoji_char = emoji_dict.get(detected_emotion, '😐')
            
            running = True
            paused = False
            
            while running and pygame.mixer.music.get_busy():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            pygame.mixer.music.pause()
                            paused = True
                            print("⏸️  Paused")
                        elif event.key == pygame.K_r:
                            pygame.mixer.music.unpause()
                            paused = False
                            print("▶️  Resumed")
                        elif event.key == pygame.K_s:
                            pygame.mixer.music.stop()
                            print("⏹️  Stopped")
                        elif event.key == pygame.K_q:
                            running = False
                            
                # Draw
                screen.fill((30, 30, 40))
                
                # Display Emoji (or fallback text if font fails)
                try:
                    emoji_surface = emoji_font.render(emoji_char, True, (255, 255, 255))
                    # Center the emoji
                    emoji_rect = emoji_surface.get_rect(center=(300, 150))
                    screen.blit(emoji_surface, emoji_rect)
                except:
                    # Fallback if emoji rendering fails
                    emoji_text = font.render(f"Emotion: {detected_emotion.title()}", True, (255, 200, 100))
                    screen.blit(emoji_text, (50, 150))

                # Song name
                song_text = font.render(f"Song: {song_name}", True, (255, 255, 255))
                song_rect = song_text.get_rect(center=(300, 250))
                screen.blit(song_text, song_rect)
                
                # Status
                status = "PAUSED" if paused else "PLAYING"
                status_color = (255, 200, 100) if paused else (100, 255, 100)
                status_text = font.render(status, True, status_color)
                status_rect = status_text.get_rect(center=(300, 320))
                screen.blit(status_text, status_rect)
                
                # Controls hint
                hint_text = font.render("P: Pause | R: Resume | S: Stop | Q: Quit", True, (150, 150, 150))
                hint_rect = hint_text.get_rect(center=(300, 370))
                # Scale down hint text
                hint_text = pygame.transform.scale(hint_text, (int(hint_rect.width * 0.7), int(hint_rect.height * 0.7)))
                hint_rect = hint_text.get_rect(center=(300, 370))
                screen.blit(hint_text, hint_rect)
                
                pygame.display.flip()
                clock.tick(30)
                
            pygame.mixer.music.stop()
            pygame.quit()
            print("\n✅ Playback finished")
            
        except Exception as e:
            print(f"⚠️  Error playing music: {e}")
            
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("🎵 MULTIMODAL EMOTION-BASED MUSIC PLAYER")
        print("="*60)
        print("\nThis system detects your emotions from multiple sources:")
        print("  📹 Facial expressions (webcam)")
        print("  🎤 Voice/audio (microphone)")
        print("  💬 Text input (optional)")
        print("\nThen recommends and plays music matching your mood!\n")
        
        input("Press Enter to start...")
        
        # Detect emotions from all modalities
        facial_probs, audio_probs, text_probs = self.detect_emotions(
            use_facial=True,
            use_audio=True,
            use_text=True
        )
        
        # Fuse and get recommendation
        detected_emotion, song = self.fuse_and_recommend(facial_probs, audio_probs, text_probs)
        
        # Play music
        if song:
            self.play_music(song, detected_emotion)
        else:
            print("⚠️  Could not find a suitable song")
            
        print("\n👋 Thank you for using the Multimodal Music Player!")

def main():
    try:
        player = MultimodalMusicPlayer()
        player.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
