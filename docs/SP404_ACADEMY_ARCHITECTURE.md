# SP404 ACADEMY - Complete System Architecture
**Interactive Learning Platform for Roland SP-404MK2**

---

## Executive Summary

**Product**: AI-powered interactive music production course platform
**Market**: SP-404MK2 owners (60,000+ units sold since 2021)
**Revenue Model**: Freemium ($0 basic / $15/month premium / $99 lifetime)
**Tech Stack**: React/Next.js + FastAPI + Pydantic AI + Qwen 3
**Unique Value**: First platform with Web MIDI hardware integration for real-time performance feedback

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js 14)                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐   │
│  │ Lesson Player  │  │ MIDI Tracker   │  │ Progress Dashboard │   │
│  │ (Video + AI)   │  │ (Web MIDI API) │  │ (Achievements)     │   │
│  └────────────────┘  └────────────────┘  └────────────────────┘   │
└──────────────┬──────────────────┬────────────────┬─────────────────┘
               │                  │                │
               ▼                  ▼                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      FASTAPI MICROSERVICES                            │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ 1. LESSON CONTENT SERVICE (Pydantic AI + Qwen 3)                │ │
│  │    - AI exercise generation                                     │ │
│  │    - Difficulty adaptation                                      │ │
│  │    - Content versioning                                         │ │
│  ├─────────────────────────────────────────────────────────────────┤ │
│  │ 2. MIDI INTEGRATION SERVICE (Pure Python)                       │ │
│  │    - WebSocket MIDI relay                                       │ │
│  │    - Performance recording                                      │ │
│  │    - Real-time event processing                                 │ │
│  ├─────────────────────────────────────────────────────────────────┤ │
│  │ 3. PERFORMANCE EVALUATION SERVICE (Pydantic AI + Qwen 3)        │ │
│  │    - Rhythm accuracy scoring                                    │ │
│  │    - AI feedback generation                                     │ │
│  │    - Weakness detection                                         │ │
│  ├─────────────────────────────────────────────────────────────────┤ │
│  │ 4. USER PROGRESSION SERVICE (Autonomous Agent Pattern)          │ │
│  │    - Adaptive curriculum                                        │ │
│  │    - Next lesson recommendation                                 │ │
│  │    - Skill tree management                                      │ │
│  ├─────────────────────────────────────────────────────────────────┤ │
│  │ 5. SAMPLE INTEGRATION SERVICE (EXISTING!)                       │ │
│  │    - Sample discovery                                           │ │
│  │    - Kit generation                                             │ │
│  │    - BPM/key analysis                                           │ │
│  ├─────────────────────────────────────────────────────────────────┤ │
│  │ 6. SUBSCRIPTION SERVICE (Stripe + Clerk Auth)                   │ │
│  │    - Payment processing                                         │ │
│  │    - Access control                                             │ │
│  │    - Usage analytics                                            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐               │
│  │ PostgreSQL  │  │ Cloudflare R2│  │ Redis Cache │               │
│  │ (Supabase)  │  │ (Samples)    │  │             │               │
│  └─────────────┘  └──────────────┘  └─────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Subsystem 1: Lesson Content System
**Pattern**: Orchestrator-Workers (Content Generation)
**LLM**: Qwen 3 via Pydantic AI

### Architecture

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# Custom OpenRouter model wrapper
class QwenModel(OpenAIModel):
    def __init__(self, model_name: str = "qwen/qwen-2.5-72b-instruct"):
        super().__init__(
            model_name=model_name,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

# Lesson generator agent
lesson_agent = Agent(
    model=QwenModel(),
    result_type=LessonContent,
    system_prompt="""You are an expert SP-404MK2 instructor.
    Generate engaging, practical exercises that teach specific techniques.
    Focus on rhythm, sampling, effects, and beat-making fundamentals."""
)

@dataclass
class LessonContent:
    title: str
    difficulty: str  # beginner, intermediate, advanced
    objectives: List[str]
    instructions: str
    exercise_sequence: List[ExerciseStep]
    success_criteria: Dict[str, Any]
    estimated_time: int  # minutes
```

### Exercise Generation Flow

```python
# app/services/lesson_content_service.py
class LessonContentService:
    """Orchestrates AI-powered lesson generation"""

    async def generate_lesson(
        self,
        topic: str,
        skill_level: str,
        previous_performance: Optional[PerformanceData] = None
    ) -> Lesson:
        """
        Generate adaptive lesson content based on user skill.

        Uses Pydantic AI Agent pattern for structured output.
        """
        # Prepare context with user history
        context = {
            "topic": topic,
            "skill_level": skill_level,
            "previous_scores": previous_performance.scores if previous_performance else None,
            "weak_areas": self._identify_weaknesses(previous_performance)
        }

        # Call Qwen 3 via Pydantic AI
        result = await lesson_agent.run(
            f"Generate a {skill_level} lesson on {topic}",
            context=context
        )

        # Save to database
        lesson = Lesson(
            title=result.data.title,
            content=result.data.model_dump(),
            difficulty=skill_level,
            ai_model="qwen-2.5-72b",
            generation_cost=result.usage.total_cost
        )

        await self.db.save(lesson)
        return lesson

    async def generate_exercise_variations(
        self,
        base_exercise: Exercise,
        num_variations: int = 5
    ) -> List[Exercise]:
        """Generate variations of successful exercises"""
        # Use Pydantic AI to create similar but unique exercises
        pass
```

### Database Schema

```sql
CREATE TABLE lessons (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    topic VARCHAR(100),  -- rhythm, sampling, effects, sequencing
    difficulty VARCHAR(20),  -- beginner, intermediate, advanced
    content JSONB,  -- Full LessonContent structure
    objectives TEXT[],
    estimated_minutes INT,

    -- AI metadata
    ai_model VARCHAR(50),
    generation_cost DECIMAL(10, 6),
    generated_at TIMESTAMP DEFAULT NOW(),

    -- Access control
    tier VARCHAR(20) DEFAULT 'premium',  -- free, premium, lifetime

    -- Engagement metrics
    completion_count INT DEFAULT 0,
    average_score DECIMAL(4, 2),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE exercises (
    id UUID PRIMARY KEY,
    lesson_id UUID REFERENCES lessons(id),
    sequence_order INT,

    -- Exercise definition
    type VARCHAR(50),  -- rhythm_pattern, sample_chop, effect_chain, sequence_build
    instructions TEXT,
    target_pattern JSONB,  -- Expected MIDI/timing data

    -- Grading criteria
    timing_tolerance_ms INT DEFAULT 50,
    velocity_tolerance INT DEFAULT 20,
    min_accuracy_percent INT DEFAULT 70,

    -- AI generation
    ai_generated BOOLEAN DEFAULT FALSE,
    parent_exercise_id UUID REFERENCES exercises(id),  -- For variations

    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Subsystem 2: MIDI Integration Engine
**Pattern**: Event-Driven Real-time Processing
**LLM**: None (Pure JavaScript + Python)

### Web MIDI API Implementation (Frontend)

```typescript
// lib/midi/sp404-connector.ts
export class SP404MIDIConnector {
  private midiAccess: MIDIAccess | null = null;
  private sp404Input: MIDIInput | null = null;
  private listeners: Map<string, Set<MIDIMessageHandler>> = new Map();

  async connect(): Promise<boolean> {
    try {
      // Request MIDI access (requires HTTPS + user permission)
      this.midiAccess = await navigator.requestMIDIAccess();

      // Find SP-404MK2 device
      this.sp404Input = this.findSP404Device();

      if (!this.sp404Input) {
        throw new Error("SP-404MK2 not found. Check USB connection.");
      }

      // Listen for MIDI messages
      this.sp404Input.onmidimessage = (event) => this.handleMIDIMessage(event);

      return true;
    } catch (error) {
      console.error("MIDI connection failed:", error);
      return false;
    }
  }

  private findSP404Device(): MIDIInput | null {
    for (const input of this.midiAccess!.inputs.values()) {
      // SP-404MK2 appears as "SP-404MKII" in MIDI device list
      if (input.name?.includes("SP-404") || input.name?.includes("SP404")) {
        return input;
      }
    }
    return null;
  }

  private handleMIDIMessage(event: MIDIMessageEvent) {
    const [status, note, velocity] = event.data;

    // Parse MIDI message
    const messageType = status & 0xF0;
    const channel = status & 0x0F;

    if (messageType === 0x90 && velocity > 0) {
      // Note On (pad hit)
      const padNumber = this.noteToPadNumber(note);
      this.emit('pad-hit', {
        pad: padNumber,
        velocity,
        timestamp: event.timeStamp,
        channel
      });
    } else if (messageType === 0x80 || (messageType === 0x90 && velocity === 0)) {
      // Note Off (pad release)
      const padNumber = this.noteToPadNumber(note);
      this.emit('pad-release', {
        pad: padNumber,
        timestamp: event.timeStamp
      });
    } else if (messageType === 0xF8) {
      // MIDI Clock (for tempo sync)
      this.emit('clock-tick', { timestamp: event.timeStamp });
    }
  }

  private noteToPadNumber(midiNote: number): number {
    // SP-404MK2 MIDI Mode A: Pads 1-16 = Notes 36-51
    if (midiNote >= 36 && midiNote <= 51) {
      return midiNote - 35;  // Pad 1-16
    }
    // Mode B: Different mapping
    return -1;
  }

  on(event: string, handler: MIDIMessageHandler): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
  }

  private emit(event: string, data: any): void {
    const handlers = this.listeners.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }
}

// Usage in React component
export function ExercisePlayer({ exercise }: { exercise: Exercise }) {
  const [midi] = useState(() => new SP404MIDIConnector());
  const [performance, setPerformance] = useState<PerformanceData>({ hits: [] });

  useEffect(() => {
    midi.connect().then(connected => {
      if (!connected) {
        alert("Connect your SP-404MK2 via USB");
      }
    });

    midi.on('pad-hit', (data) => {
      // Record performance data
      setPerformance(prev => ({
        hits: [...prev.hits, {
          pad: data.pad,
          velocity: data.velocity,
          timestamp: data.timestamp,
          expectedTimestamp: getExpectedTime(exercise, prev.hits.length)
        }]
      }));

      // Send to backend for real-time scoring
      socket.emit('midi-event', data);
    });

    return () => midi.disconnect();
  }, []);

  return (
    <div>
      <PadVisualizer performance={performance} />
      <ScoreDisplay score={calculateScore(performance, exercise)} />
    </div>
  );
}
```

### Backend MIDI Processing (FastAPI)

```python
# app/services/midi_processing_service.py
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class MIDIEvent:
    pad: int
    velocity: int
    timestamp: float  # milliseconds
    expected_timestamp: Optional[float] = None

class MIDIProcessingService:
    """Process MIDI events for performance evaluation"""

    def calculate_timing_accuracy(
        self,
        events: List[MIDIEvent],
        target_pattern: List[float],
        tolerance_ms: int = 50
    ) -> float:
        """
        Calculate rhythm accuracy percentage.

        Args:
            events: Recorded MIDI events
            target_pattern: Expected timestamps
            tolerance_ms: Allowable timing error

        Returns:
            Accuracy percentage (0-100)
        """
        if len(events) != len(target_pattern):
            return 0.0

        errors = []
        for event, expected_time in zip(events, target_pattern):
            error = abs(event.timestamp - expected_time)
            errors.append(error)

        # Calculate hits within tolerance
        accurate_hits = sum(1 for error in errors if error <= tolerance_ms)
        accuracy = (accurate_hits / len(errors)) * 100

        return round(accuracy, 2)

    def calculate_velocity_consistency(
        self,
        events: List[MIDIEvent]
    ) -> float:
        """
        Measure velocity consistency (important for dynamics control).

        Returns:
            Consistency score (0-100), where 100 = perfectly even
        """
        if len(events) < 2:
            return 100.0

        velocities = [e.velocity for e in events]
        std_dev = np.std(velocities)

        # Convert std dev to 0-100 score (lower std = higher score)
        # Max std dev of 30 = score of 0
        consistency = max(0, 100 - (std_dev / 30 * 100))

        return round(consistency, 2)

    def detect_rhythm_pattern(
        self,
        events: List[MIDIEvent]
    ) -> str:
        """
        Identify the rhythm pattern being played.

        Returns:
            Pattern name (e.g., "straight_8ths", "swing_16ths", "triplets")
        """
        if len(events) < 4:
            return "unknown"

        # Calculate inter-onset intervals (IOI)
        intervals = []
        for i in range(len(events) - 1):
            interval = events[i + 1].timestamp - events[i].timestamp
            intervals.append(interval)

        avg_interval = np.mean(intervals)

        # Classify pattern based on average interval
        if 400 <= avg_interval <= 600:  # ~120 BPM quarter notes
            return "quarter_notes"
        elif 200 <= avg_interval <= 300:  # 8th notes
            return "eighth_notes"
        elif 100 <= avg_interval <= 150:  # 16th notes
            return "sixteenth_notes"

        return "custom_pattern"

    async def record_performance(
        self,
        user_id: int,
        exercise_id: int,
        events: List[MIDIEvent]
    ) -> Performance:
        """Save performance to database for history tracking"""
        performance = Performance(
            user_id=user_id,
            exercise_id=exercise_id,
            midi_events=json.dumps([asdict(e) for e in events]),
            timing_accuracy=self.calculate_timing_accuracy(events, ...),
            velocity_consistency=self.calculate_velocity_consistency(events),
            completed_at=datetime.utcnow()
        )

        await self.db.save(performance)
        return performance
```

### WebSocket Real-Time Communication

```python
# app/api/v1/endpoints/midi_stream.py
from fastapi import WebSocket, WebSocketDisconnect

@router.websocket("/ws/exercise/{exercise_id}")
async def exercise_stream(
    websocket: WebSocket,
    exercise_id: int,
    current_user: User = Depends(get_current_user_ws)
):
    """
    Real-time MIDI event streaming and scoring.

    Flow:
    1. Frontend sends MIDI events as they happen
    2. Backend calculates running score
    3. Backend sends real-time feedback
    """
    await websocket.accept()

    # Load exercise target pattern
    exercise = await ExerciseService.get(exercise_id)
    midi_service = MIDIProcessingService()

    performance_events = []

    try:
        while True:
            # Receive MIDI event from frontend
            data = await websocket.receive_json()

            event = MIDIEvent(
                pad=data['pad'],
                velocity=data['velocity'],
                timestamp=data['timestamp']
            )
            performance_events.append(event)

            # Calculate current score
            current_score = midi_service.calculate_timing_accuracy(
                performance_events,
                exercise.target_pattern[:len(performance_events)]
            )

            # Send real-time feedback
            await websocket.send_json({
                "type": "score_update",
                "score": current_score,
                "event_count": len(performance_events),
                "feedback": "Great timing!" if current_score > 90 else "Keep practicing!"
            })

    except WebSocketDisconnect:
        # Save final performance
        await midi_service.record_performance(
            user_id=current_user.id,
            exercise_id=exercise_id,
            events=performance_events
        )
```

---

## Subsystem 3: Performance Evaluation Service
**Pattern**: Evaluator-Optimizer (Score → Feedback → Adapt)
**LLM**: Qwen 3 for personalized feedback

### AI Feedback Generation

```python
# app/services/performance_evaluation_service.py
from pydantic_ai import Agent

# Performance feedback agent
feedback_agent = Agent(
    model=QwenModel("qwen/qwen-2.5-72b-instruct"),
    result_type=PerformanceFeedback,
    system_prompt="""You are an encouraging music production coach.
    Analyze student performance data and provide:
    1. Specific praise for what they did well
    2. Constructive tips for improvement (max 2-3 points)
    3. Motivation to keep practicing

    Be supportive but honest. Use music production terminology."""
)

@dataclass
class PerformanceFeedback:
    overall_score: int  # 0-100
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_tips: List[str]
    encouragement: str
    next_steps: List[str]

class PerformanceEvaluationService:
    """Evaluate student performance and generate AI feedback"""

    async def evaluate_performance(
        self,
        performance: Performance,
        exercise: Exercise
    ) -> Evaluation:
        """
        Complete performance evaluation with AI feedback.

        Combines:
        - Quantitative metrics (timing, velocity)
        - Qualitative AI analysis
        - Personalized recommendations
        """
        # Calculate objective metrics
        metrics = {
            "timing_accuracy": self._score_timing(performance, exercise),
            "velocity_consistency": self._score_velocity(performance),
            "pattern_recognition": self._score_pattern(performance, exercise),
            "tempo_stability": self._score_tempo(performance)
        }

        # Overall score (weighted average)
        overall_score = (
            metrics["timing_accuracy"] * 0.4 +
            metrics["velocity_consistency"] * 0.2 +
            metrics["pattern_recognition"] * 0.3 +
            metrics["tempo_stability"] * 0.1
        )

        # Generate AI feedback
        context = {
            "metrics": metrics,
            "overall_score": overall_score,
            "exercise_difficulty": exercise.difficulty,
            "previous_attempts": await self._get_previous_attempts(performance.user_id, exercise.id)
        }

        feedback_result = await feedback_agent.run(
            f"Provide feedback for exercise '{exercise.title}' with score {overall_score}",
            context=context
        )

        # Save evaluation
        evaluation = Evaluation(
            performance_id=performance.id,
            overall_score=overall_score,
            timing_score=metrics["timing_accuracy"],
            velocity_score=metrics["velocity_consistency"],
            pattern_score=metrics["pattern_recognition"],
            tempo_score=metrics["tempo_stability"],
            feedback=feedback_result.data.model_dump(),
            ai_model="qwen-2.5-72b",
            evaluation_cost=feedback_result.usage.total_cost,
            created_at=datetime.utcnow()
        )

        await self.db.save(evaluation)
        return evaluation

    def _score_timing(self, performance: Performance, exercise: Exercise) -> float:
        """Score timing accuracy (0-100)"""
        events = json.loads(performance.midi_events)
        target = exercise.target_pattern

        # Calculate average timing error
        errors = []
        for i, event in enumerate(events):
            if i < len(target):
                error = abs(event['timestamp'] - target[i])
                errors.append(error)

        avg_error = np.mean(errors)

        # Convert to 0-100 score
        # 0ms error = 100, 100ms error = 50, 200ms+ = 0
        score = max(0, 100 - (avg_error / 2))
        return round(score, 2)

    async def generate_improvement_plan(
        self,
        user_id: int,
        weak_areas: List[str]
    ) -> List[Exercise]:
        """
        Generate targeted exercises to improve weak areas.

        Uses AI to create custom practice routines.
        """
        # Use lesson_agent to generate targeted content
        pass
```

### Database Schema

```sql
CREATE TABLE performances (
    id UUID PRIMARY KEY,
    user_id INT REFERENCES users(id),
    exercise_id UUID REFERENCES exercises(id),

    -- MIDI recording
    midi_events JSONB,  -- Full MIDI event sequence
    duration_seconds INT,

    -- Quick metrics
    timing_accuracy DECIMAL(5, 2),
    velocity_consistency DECIMAL(5, 2),

    completed_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_exercise (user_id, exercise_id)
);

CREATE TABLE evaluations (
    id UUID PRIMARY KEY,
    performance_id UUID REFERENCES performances(id),

    -- Scores (0-100)
    overall_score DECIMAL(5, 2),
    timing_score DECIMAL(5, 2),
    velocity_score DECIMAL(5, 2),
    pattern_score DECIMAL(5, 2),
    tempo_score DECIMAL(5, 2),

    -- AI feedback
    feedback JSONB,  -- PerformanceFeedback structure
    ai_model VARCHAR(50),
    evaluation_cost DECIMAL(10, 6),

    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Subsystem 4: User Progression System
**Pattern**: Autonomous Agent (Adaptive Curriculum)
**LLM**: Qwen 3 for next lesson recommendation

### Adaptive Curriculum Agent

```python
# app/services/progression_service.py
from pydantic_ai import Agent

# Curriculum planning agent
curriculum_agent = Agent(
    model=QwenModel("qwen/qwen-2.5-72b-instruct"),
    result_type=CurriculumPlan,
    system_prompt="""You are an intelligent curriculum designer for SP-404MK2.
    Analyze student performance history and recommend the optimal next lesson.

    Principles:
    - Build on mastered skills
    - Target weak areas without overwhelming
    - Maintain motivation with variety
    - Progress difficulty gradually (no big jumps)
    - Unlock advanced techniques after fundamentals are solid"""
)

@dataclass
class CurriculumPlan:
    next_lesson_id: str
    reasoning: str
    prerequisites_met: bool
    estimated_success_rate: int  # 0-100
    alternative_lessons: List[str]
    skill_tree_path: List[str]

class ProgressionService:
    """Manage adaptive student curriculum"""

    async def get_next_lesson(
        self,
        user_id: int
    ) -> Lesson:
        """
        Determine the next lesson for a student.

        Uses AI agent to analyze:
        - Completed lessons
        - Performance scores
        - Time since last practice
        - Weak areas
        - Interest signals (repeated lessons)
        """
        # Gather student context
        completed = await self.db.get_completed_lessons(user_id)
        recent_scores = await self.db.get_recent_scores(user_id, limit=10)
        weak_skills = self._identify_weak_skills(recent_scores)

        context = {
            "completed_lessons": [l.id for l in completed],
            "average_score": np.mean([s.overall_score for s in recent_scores]),
            "weak_skills": weak_skills,
            "days_since_last_practice": self._days_since_practice(user_id)
        }

        # Ask AI for recommendation
        result = await curriculum_agent.run(
            "Recommend the next lesson for this student",
            context=context
        )

        # Fetch recommended lesson
        next_lesson = await self.db.get_lesson(result.data.next_lesson_id)

        # Log recommendation
        await self.db.log_recommendation(
            user_id=user_id,
            lesson_id=next_lesson.id,
            reasoning=result.data.reasoning,
            ai_model="qwen-2.5-72b"
        )

        return next_lesson

    def _identify_weak_skills(
        self,
        recent_scores: List[Evaluation]
    ) -> List[str]:
        """Identify skills that need improvement"""
        skill_scores = defaultdict(list)

        for eval in recent_scores:
            # Group scores by skill category
            skill_scores['timing'].append(eval.timing_score)
            skill_scores['velocity'].append(eval.velocity_score)
            skill_scores['pattern'].append(eval.pattern_score)

        # Find skills below 70% average
        weak_skills = []
        for skill, scores in skill_scores.items():
            if np.mean(scores) < 70:
                weak_skills.append(skill)

        return weak_skills

    async def update_skill_tree(
        self,
        user_id: int,
        completed_lesson: Lesson,
        score: float
    ):
        """
        Update student's skill tree based on completed lesson.

        Unlocks new lessons if prerequisites are met.
        """
        # Mark lesson complete
        await self.db.mark_complete(user_id, completed_lesson.id)

        # Check for skill mastery (3 consecutive attempts at 80%+)
        if await self._check_mastery(user_id, completed_lesson.topic):
            await self.db.unlock_advanced_lessons(user_id, completed_lesson.topic)

            # Send achievement notification
            await self.notifications.send(
                user_id,
                f"🎉 Mastered {completed_lesson.topic}! Advanced lessons unlocked."
            )
```

### Skill Tree Database

```sql
CREATE TABLE skill_tree (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE,  -- "basic_rhythm", "sampling_101", etc.
    description TEXT,
    difficulty INT,  -- 1-10

    -- Prerequisites (can be multiple)
    requires_skills UUID[] DEFAULT '{}',

    -- Associated lessons
    lessons UUID[] DEFAULT '{}'
);

CREATE TABLE user_skills (
    user_id INT REFERENCES users(id),
    skill_id UUID REFERENCES skill_tree(id),

    status VARCHAR(20),  -- locked, available, in_progress, mastered
    mastery_score DECIMAL(5, 2),  -- Average of last 3 attempts
    attempts INT DEFAULT 0,

    unlocked_at TIMESTAMP,
    mastered_at TIMESTAMP,

    PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE lesson_recommendations (
    id UUID PRIMARY KEY,
    user_id INT REFERENCES users(id),
    lesson_id UUID REFERENCES lessons(id),

    reasoning TEXT,  -- AI explanation
    estimated_success INT,  -- 0-100
    ai_model VARCHAR(50),

    accepted BOOLEAN,  -- Did user start the lesson?

    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_created (user_id, created_at DESC)
);
```

---

## Subsystem 5: Sample Integration
**Status**: ✅ ALREADY BUILT!

This subsystem exists in the current codebase:
- **HybridAnalysisService**: Audio + AI vibe analysis
- **SP404ExportService**: Hardware-compatible export
- **Sample database**: 760+ samples with BPM/key/genre

### Integration Points

```python
# app/services/lesson_sample_service.py
class LessonSampleService:
    """Bridge between lessons and sample library"""

    async def get_samples_for_lesson(
        self,
        lesson: Lesson,
        user_preferences: Optional[Dict] = None
    ) -> List[Sample]:
        """
        Find relevant samples for a lesson.

        Example: "Lo-Fi Beat Making" lesson gets mellow samples at 80-95 BPM
        """
        # Extract lesson requirements
        if lesson.topic == "lo_fi_beat_making":
            query = {
                "genre": "hip-hop",
                "bpm_min": 80,
                "bpm_max": 95,
                "vibe_tags": ["mellow", "warm", "vintage"]
            }
        elif lesson.topic == "trap_drums":
            query = {
                "genre": "trap",
                "tags": ["kick", "snare", "hihat"],
                "bpm_min": 130,
                "bpm_max": 150
            }

        # Query existing sample database
        samples = await self.sample_repo.search(query, limit=16)

        return samples

    async def generate_practice_kit(
        self,
        lesson: Lesson
    ) -> Kit:
        """
        Auto-generate an 8-piece kit for practicing this lesson.

        Uses existing KitAssembler from sample pipeline.
        """
        samples = await self.get_samples_for_lesson(lesson)

        # Use existing kit builder
        from src.tools.kit_assembler import KitAssembler
        assembler = KitAssembler()

        kit = await assembler.generate_kit(
            name=f"{lesson.title} Practice Kit",
            output_dir=f"/tmp/lesson_kits/{lesson.id}",
            samples=samples,
            max_samples=8,
            format="wav"
        )

        return kit
```

---

## Subsystem 6: Subscription & Payments
**Pattern**: Prompt Chaining (Signup → Subscribe → Access)
**LLM**: None (Stripe + Clerk)

### Freemium Tiers

```typescript
// lib/subscription/tiers.ts
export const SUBSCRIPTION_TIERS = {
  free: {
    name: "Free",
    price: 0,
    features: [
      "5 beginner lessons",
      "Basic rhythm exercises",
      "Community forum access",
      "Limited sample library (50 samples)"
    ],
    limits: {
      lessons_per_month: 5,
      samples_downloads: 10,
      kit_exports: 2
    }
  },

  premium: {
    name: "Premium",
    price: 15,  // $15/month
    stripe_price_id: "price_xxxxx",
    features: [
      "Unlimited lessons (all levels)",
      "AI performance feedback",
      "Full sample library (10,000+ samples)",
      "Unlimited kit exports",
      "Progress tracking & analytics",
      "Priority support"
    ],
    limits: {
      lessons_per_month: -1,  // unlimited
      samples_downloads: -1,
      kit_exports: -1
    }
  },

  lifetime: {
    name: "Lifetime",
    price: 99,  // $99 one-time
    stripe_price_id: "price_yyyyy",
    features: [
      "All Premium features",
      "Lifetime access",
      "Early access to new lessons",
      "Exclusive community Discord",
      "Custom lesson requests (1/month)"
    ]
  }
};
```

### Stripe Integration

```python
# app/services/subscription_service.py
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionService:
    """Manage subscriptions and access control"""

    async def create_checkout_session(
        self,
        user_id: int,
        tier: str  # "premium" or "lifetime"
    ) -> str:
        """
        Create Stripe checkout session.

        Returns: Checkout URL to redirect user to
        """
        user = await self.db.get_user(user_id)

        # Get price ID for tier
        if tier == "premium":
            price_id = settings.STRIPE_PREMIUM_PRICE_ID
            mode = "subscription"
        elif tier == "lifetime":
            price_id = settings.STRIPE_LIFETIME_PRICE_ID
            mode = "payment"
        else:
            raise ValueError(f"Invalid tier: {tier}")

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            mode=mode,
            success_url=f"{settings.APP_URL}/subscribe/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.APP_URL}/subscribe/cancel",
            metadata={
                "user_id": user_id,
                "tier": tier
            }
        )

        return session.url

    async def handle_webhook(
        self,
        payload: bytes,
        sig_header: str
    ):
        """
        Handle Stripe webhooks (payment success, subscription cancel, etc.)
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            await self._handle_successful_payment(session)

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            await self._handle_subscription_cancel(subscription)

    async def _handle_successful_payment(self, session: dict):
        """Activate subscription after successful payment"""
        user_id = int(session["metadata"]["user_id"])
        tier = session["metadata"]["tier"]

        # Update user tier
        await self.db.update_user(user_id, {
            "subscription_tier": tier,
            "subscribed_at": datetime.utcnow(),
            "stripe_customer_id": session.get("customer")
        })

        # Send welcome email
        await self.email.send_welcome(user_id, tier)

    async def check_access(
        self,
        user_id: int,
        lesson_id: UUID
    ) -> bool:
        """Check if user can access a lesson"""
        user = await self.db.get_user(user_id)
        lesson = await self.db.get_lesson(lesson_id)

        # Free tier check
        if user.subscription_tier == "free":
            if lesson.tier == "free":
                return True

            # Check monthly limit
            lessons_this_month = await self.db.count_lessons_this_month(user_id)
            if lessons_this_month >= SUBSCRIPTION_TIERS["free"]["limits"]["lessons_per_month"]:
                return False

        # Premium/Lifetime have full access
        return user.subscription_tier in ["premium", "lifetime"]
```

### Clerk Authentication

```typescript
// lib/auth/clerk.ts
import { ClerkProvider } from '@clerk/nextjs';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      appearance={{
        elements: {
          formButtonPrimary: "bg-primary hover:bg-primary-focus",
          card: "bg-base-100 shadow-xl"
        }
      }}
    >
      {children}
    </ClerkProvider>
  );
}

// Middleware for protected routes
export async function requireAuth(req: NextRequest) {
  const { userId } = auth();

  if (!userId) {
    return NextResponse.redirect(new URL('/sign-in', req.url));
  }

  return NextResponse.next();
}
```

---

## Complete Tech Stack Summary

### Frontend
```
- Next.js 14 (App Router)
- React 18 + TypeScript
- TailwindCSS + DaisyUI
- Web MIDI API (native browser)
- Clerk (authentication)
- Stripe React (payments)
- React Query (data fetching)
- Zustand (state management)
- Recharts (analytics dashboards)
```

### Backend
```
- FastAPI (Python 3.11+)
- Pydantic AI (LLM orchestration)
- Qwen 3 via OpenRouter (AI generation)
- PostgreSQL + SQLAlchemy
- Redis (caching + sessions)
- Celery (background jobs)
- Stripe (payments)
- WebSocket (real-time)
```

### Infrastructure
```
- Vercel (Next.js hosting)
- Railway / Fly.io (FastAPI)
- Supabase (PostgreSQL + auth)
- Cloudflare R2 (sample storage)
- Redis Cloud (caching)
- GitHub Actions (CI/CD)
```

---

## MVP Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Basic authentication and lesson player

- [ ] Set up Next.js 14 with Clerk auth
- [ ] Create FastAPI service structure
- [ ] Set up Supabase PostgreSQL
- [ ] Design database schema (all tables)
- [ ] Build lesson player UI (video + instructions)
- [ ] Create 5 beginner lessons (manual content)

**Deliverable**: Users can sign up and watch lesson videos

---

### Phase 2: MIDI Integration (Weeks 3-4)
**Goal**: Connect SP-404MK2 and record performances

- [ ] Implement Web MIDI API connector
- [ ] Build pad visualizer component
- [ ] Create WebSocket connection for real-time events
- [ ] Build MIDI processing service (FastAPI)
- [ ] Create first rhythm exercise (simple 4/4 pattern)
- [ ] Test with real SP-404MK2 hardware

**Deliverable**: Users can connect SP-404 and play along with exercises

---

### Phase 3: AI Evaluation (Weeks 5-6)
**Goal**: Score performances and give feedback

- [ ] Integrate Pydantic AI with Qwen 3
- [ ] Build performance evaluation service
- [ ] Create feedback agent with prompts
- [ ] Design scoring algorithm (timing + velocity)
- [ ] Build evaluation results UI
- [ ] Test with 10 beta users

**Deliverable**: AI scores performances and gives personalized feedback

---

### Phase 4: Progression System (Weeks 7-8)
**Goal**: Adaptive curriculum and skill tracking

- [ ] Build skill tree database structure
- [ ] Create progression service with AI recommendations
- [ ] Design progress dashboard UI
- [ ] Implement achievement system
- [ ] Create 20 total lessons (beginner to intermediate)
- [ ] Build curriculum agent

**Deliverable**: Students get personalized lesson recommendations

---

### Phase 5: Sample Integration (Week 9)
**Goal**: Connect to existing sample library

- [ ] Build lesson-sample bridge service
- [ ] Auto-generate practice kits for each lesson
- [ ] Create sample browser in lesson UI
- [ ] Test with existing 760-sample database
- [ ] Build download/export flow

**Deliverable**: Each lesson has curated practice samples

---

### Phase 6: Subscription & Launch (Weeks 10-12)
**Goal**: Launch freemium product

- [ ] Integrate Stripe checkout
- [ ] Implement access control middleware
- [ ] Create pricing page
- [ ] Set up webhook handlers
- [ ] Build admin dashboard (lesson management)
- [ ] Beta test with 50 users
- [ ] Launch Product Hunt campaign
- [ ] Create marketing site

**Deliverable**: Public launch with paying customers

---

## Business Model Projections

### Pricing Strategy
- **Free**: 5 beginner lessons (lead magnet)
- **Premium**: $15/month (target: 70% of conversions)
- **Lifetime**: $99 one-time (target: 30% of conversions)

### Revenue Projections (Year 1)

**Conservative Scenario** (100 paying users):
```
70 users x $15/month x 12 months = $12,600
30 users x $99 lifetime        =  $2,970
Total:                           $15,570
```

**Moderate Scenario** (500 paying users):
```
350 users x $15/month x 12 months = $63,000
150 users x $99 lifetime          = $14,850
Total:                             $77,850
```

**Optimistic Scenario** (2,000 paying users):
```
1,400 users x $15/month x 12 months = $252,000
600 users x $99 lifetime            =  $59,400
Total:                               $311,400
```

### Cost Structure (Monthly)
```
Infrastructure (Vercel + Railway + Supabase): $100
OpenRouter AI costs (2000 users x 50 lessons):  $50
Stripe fees (2.9% + $0.30):                    ~$800
Marketing:                                    $1,000
Total:                                       ~$1,950
```

**Target**: 100 paying users to break even ($1,500 MRR)

---

## Key Success Metrics

### User Engagement
- **Lesson Completion Rate**: Target 60%+ (industry avg: 40%)
- **Weekly Active Users**: Target 40% of subscribers
- **Average Session Length**: Target 20+ minutes
- **Practice Frequency**: Target 3x/week

### Product Performance
- **MIDI Latency**: <50ms (critical for rhythm training)
- **AI Feedback Generation**: <3 seconds
- **Lesson Load Time**: <2 seconds
- **Exercise Grading Accuracy**: 95%+ validated

### Business Metrics
- **Free to Paid Conversion**: Target 5% (industry avg: 2-3%)
- **Monthly Churn**: Target <5%
- **Lifetime Value (LTV)**: Target $300+
- **Customer Acquisition Cost (CAC)**: Target <$30

---

## Competitive Advantages

1. **First SP-404-Specific Platform**: No direct competitors
2. **Hardware Integration**: Melodics doesn't support SP-404
3. **AI-Powered Adaptation**: Personalized learning path
4. **Sample Library Integration**: Learn with real samples
5. **Freemium Model**: Low barrier to entry

---

## Technical Risks & Mitigations

### Risk 1: Web MIDI Browser Support
**Issue**: Safari/iOS don't support Web MIDI
**Impact**: ~30% of potential users
**Mitigation**:
- Desktop-first launch (Chrome/Edge)
- Build iOS app later (Core MIDI API)
- Offer MIDI file upload alternative

### Risk 2: AI Generation Costs
**Issue**: Qwen 3 costs could scale with users
**Impact**: Margin compression
**Mitigation**:
- Cache generated content aggressively
- Use cheaper 7B model for simple tasks
- Pre-generate common exercises
- Monitor cost per user closely

### Risk 3: SP-404 MIDI Compatibility
**Issue**: Firmware updates could break integration
**Impact**: Platform stops working
**Mitigation**:
- Test with multiple firmware versions
- Build version detection
- Maintain compatibility layer
- Community testing program

### Risk 4: Content Quality
**Issue**: AI-generated lessons might be low quality
**Impact**: Poor user experience
**Mitigation**:
- Human review process for all AI content
- Continuous prompt engineering
- User feedback loop
- Expert instructor validation

---

## Next Steps - Decision Points

### Option 1: Build MVP (12 weeks)
- Solo development
- Launch with 20 lessons
- Desktop-only (Chrome/Edge)
- Manual content creation initially
- Bootstrap funding

### Option 2: Raise Pre-Seed ($100K)
- Hire 1 frontend dev
- Hire 1 content creator (SP-404 expert)
- Launch with 50 lessons
- Professional marketing
- 6-month runway

### Option 3: Partner with Roland
- Pitch as official SP-404 learning platform
- Co-marketing opportunity
- Bundled with hardware sales
- Revenue share model

---

## Questions for Next Session

1. **Do you want to start with MVP Phase 1?** (Weeks 1-2: Auth + Lesson Player)
2. **Should we prototype Web MIDI integration first?** (Build simple demo to test feasibility)
3. **Do you have access to SP-404MK2 hardware?** (Critical for testing)
4. **What's your AI budget?** (OpenRouter costs ~$0.01 per lesson generation)
5. **Solo or hire team?** (Determines timeline and scope)

Let me know which direction you want to go and we'll build it! 🎹🎵
