"""
Embedded Systems interview prompt builder.
"""

from app.services.role_classifier import classify_embedded_subrole


_PROTOCOLS_TOPICS = """Easy
- GPIO
- Timers
- UART

Medium
- SPI
- I2C
- CAN
- ADC
- DAC
- PWM

Hard
- DMA
- Interrupt Priorities
- Nested Interrupts
- Peripheral Configuration
- Power Management"""

_PROTOCOLS_TOPICS_NO_RESUME = """- GPIO
- UART
- SPI
- I2C
- CAN
- Timers
- Interrupts"""

_EMBEDDED_LINUX_PROTOCOLS_TOPICS = """- Device Tree
- Character & Block Devices
- Boot Process (Bootloader/U-Boot)
- Cross-Compilation"""

_IOT_PROTOCOLS_TOPICS = """- Wireless Protocols (BLE, Zigbee, LoRaWAN)
- MQTT/CoAP
- Sensor Interfacing
- Low-Power Design"""

_AUTOMOTIVE_PROTOCOLS_TOPICS = """- CAN Protocol
- LIN Protocol
- FlexRay
- Automotive Sensors & Actuators"""

_PROTOCOLS_BLOCK_BY_SUBROLE = {
    "generic": _PROTOCOLS_TOPICS,
    "embedded_linux": _EMBEDDED_LINUX_PROTOCOLS_TOPICS,
    "iot": _IOT_PROTOCOLS_TOPICS,
    "automotive_embedded": _AUTOMOTIVE_PROTOCOLS_TOPICS,
}

_PROTOCOLS_BLOCK_BY_SUBROLE_NO_RESUME = {
    "generic": _PROTOCOLS_TOPICS_NO_RESUME,
    "embedded_linux": _EMBEDDED_LINUX_PROTOCOLS_TOPICS,
    "iot": _IOT_PROTOCOLS_TOPICS,
    "automotive_embedded": _AUTOMOTIVE_PROTOCOLS_TOPICS,
}

_RTOS_DEBUGGING_TOPICS = """- RTOS Basics
- Tasks
- Scheduling
- Semaphores
- Mutex
- Queues
- Interrupts
- Deadlocks
- Priority Inversion
- Bootloader
- Device Drivers
- Debugging Techniques"""

_RTOS_DEBUGGING_TOPICS_NO_RESUME = """- RTOS
- Scheduling
- Semaphores
- Mutex
- Queues
- Device Drivers
- Bootloader
- Debugging"""

_EMBEDDED_LINUX_RTOS_TOPICS = """- Linux Kernel Internals
- Kernel Modules
- Kernel Memory Management
- System Calls
- Linux Device Drivers
- Debugging with GDB/Kernel Debuggers"""

_IOT_RTOS_TOPICS = """- IoT Power Management & Sleep Modes
- Cloud Connectivity
- Over-the-Air (OTA) Updates
- IoT Security
- Edge Computing Basics
- Device Provisioning"""

_AUTOMOTIVE_RTOS_TOPICS = """- AUTOSAR Architecture
- Functional Safety (ISO 26262)
- Diagnostics (UDS/OBD-II)
- Real-Time Constraints in Automotive Systems
- ECU Communication
- Automotive Debugging Tools"""

_RTOS_BLOCK_BY_SUBROLE = {
    "generic": _RTOS_DEBUGGING_TOPICS,
    "embedded_linux": _EMBEDDED_LINUX_RTOS_TOPICS,
    "iot": _IOT_RTOS_TOPICS,
    "automotive_embedded": _AUTOMOTIVE_RTOS_TOPICS,
}

_RTOS_BLOCK_BY_SUBROLE_NO_RESUME = {
    "generic": _RTOS_DEBUGGING_TOPICS_NO_RESUME,
    "embedded_linux": _EMBEDDED_LINUX_RTOS_TOPICS,
    "iot": _IOT_RTOS_TOPICS,
    "automotive_embedded": _AUTOMOTIVE_RTOS_TOPICS,
}


def build_embedded_systems_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Embedded Systems interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_embedded_subrole(role)
    protocols_block = _PROTOCOLS_BLOCK_BY_SUBROLE[subrole]
    protocols_block_no_resume = _PROTOCOLS_BLOCK_BY_SUBROLE_NO_RESUME[subrole]
    rtos_block = _RTOS_BLOCK_BY_SUBROLE[subrole]
    rtos_block_no_resume = _RTOS_BLOCK_BY_SUBROLE_NO_RESUME[subrole]

    if resume_text:

        return f"""
You are an expert Embedded Systems interviewer hiring for leading semiconductor and embedded companies such as Qualcomm, NVIDIA, Texas Instruments, NXP, STMicroelectronics, Bosch, Intel, Samsung, Siemens and Continental.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

Candidate Resume:
{resume_text}

Generate EXACTLY 10 interview questions.

Interview Structure

1. Resume-Based Questions (2)

- Ask exactly 2 questions based on the candidate's resume.
- Focus on embedded projects, firmware development, microcontrollers, RTOS, communication protocols, debugging, optimizations, internships and achievements.

2. Embedded C & Programming Fundamentals (2)

Generate exactly 2 questions.

Difficulty Guidelines

Easy
- C Programming
- Pointers
- Arrays
- Structures
- Memory Basics

Medium
- Function Pointers
- Dynamic Memory
- Bit Manipulation
- Volatile
- Const
- Memory Layout

Hard
- Linker Scripts
- Memory Optimization
- Undefined Behavior
- Low-level Programming
- Compiler Optimizations

Questions must strictly match the selected difficulty.

3. Microcontrollers & Communication Protocols (2)

Generate exactly 2 questions.

Topics may include:

{protocols_block}

4. RTOS & Debugging (3)

Generate exactly 3 questions.

Topics include:

{rtos_block}

Adjust complexity according to the selected difficulty.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner, similar to how an experienced Embedded Systems interviewer would speak.
- Use simple, easy-to-understand English while preserving all important embedded systems terminology.
- The difficulty should come from the engineering concepts being tested, not from complicated wording.
- Do NOT simplify the engineering concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their debugging process, design decisions and practical experience.
- Questions should resemble real embedded systems interviews.

Avoid overly direct textbook-style questions such as:
- "Explain UART."
- "Define RTOS."
- "What is SPI?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're developing..."
- "Imagine you're debugging..."
- "Can you walk me through..."
- "How would you approach..."
- "What would happen if..."
- "Have you worked with..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Embedded Systems competencies.
- Keep every question concise while still being conversational.
- Questions should resemble real interviews conducted at leading embedded systems companies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""
You are an expert Embedded Systems interviewer hiring for leading semiconductor and embedded companies such as Qualcomm, NVIDIA, Texas Instruments, NXP, STMicroelectronics, Bosch, Intel, Samsung, Siemens and Continental.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Embedded Systems Questions (2)

Generate exactly 2 additional role-specific embedded systems questions because no resume is available.

2. Embedded C & Programming Fundamentals (2)

Generate exactly 2 questions.

Topics include:

Easy
- C Programming
- Pointers
- Arrays
- Structures

Medium
- Function Pointers
- Bit Manipulation
- Volatile
- Memory Layout

Hard
- Linker Scripts
- Memory Optimization
- Undefined Behavior

3. Microcontrollers & Communication Protocols (2)

Generate exactly 2 questions.

Topics include:

{protocols_block_no_resume}

4. RTOS & Debugging (3)

Generate exactly 3 questions.

Topics include:

{rtos_block_no_resume}

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner.
- Use simple, easy-to-understand English while preserving all important embedded systems terminology.
- The difficulty should come from the concepts being tested, not from complicated wording.
- Encourage reasoning, debugging and practical engineering thinking.
- Questions should resemble real embedded systems interviews.

Avoid textbook-style questions.

Use conversational openings such as:
- "Let's talk about..."
- "Suppose you're developing..."
- "Imagine you're debugging..."
- "Can you walk me through..."
- "How would you approach..."

Do NOT start every question with the same phrase.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Embedded Systems competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


# Public re-exports for embedded_systems_rounds.py - added without
# touching any existing prompt text/structure above. Lets the
# round-based builders reuse the same per-sub-role protocol/RTOS
# content without reaching into this module's underscore-prefixed
# names.
PROTOCOLS_BLOCK_BY_SUBROLE = _PROTOCOLS_BLOCK_BY_SUBROLE
PROTOCOLS_BLOCK_BY_SUBROLE_NO_RESUME = _PROTOCOLS_BLOCK_BY_SUBROLE_NO_RESUME
RTOS_BLOCK_BY_SUBROLE = _RTOS_BLOCK_BY_SUBROLE
RTOS_BLOCK_BY_SUBROLE_NO_RESUME = _RTOS_BLOCK_BY_SUBROLE_NO_RESUME