<template>
  <div class="md:w-auto w-full h-auto left-0 right-0 mx-auto absolute relative">
    <div class="h-[28px] md:w-[689px] left-0 right-0 mx-auto absolute relative">
      <div class="flex abolute top-[0px] left-[0px] items-center justify-center w-[28px] h-[28px] border-2 border-[#8A8A8A] rounded-full">
        <img src="../public/img/testicon.svg" />
      </div>

      <div class="md:w-[554.74px] h-[22px] absolute md:top-[1px] top-[1px] left-[40px]">
        <p class="font-sans font-semibold md:text-base text-[12px] leading-none tracking-normal text-black">
          Тестирование
        </p>
      </div>

      <div class="absolute md:top-[5px] top-[15px] md:left-[589px] left-[40px] md:w-[554.74px] h-[22px]">
        <p class="font-sans font-semibold md:text-[16px] text-[12px] leading-none tracking-normal text-[#8A8A8A]">
          Вопрос {{ currentQuestionIndex + 1 }} из {{ testData.questions.length }}
        </p>
      </div>
    </div>

    <div class="md:w-[689px] w-full h-auto rounded-[10px] mt-[14px] bg-white absolute left-0 right-0 mx-auto">
      <div class="md:w-[637px] max-w-[90%] mt-[20px] ml-[20px]">
        <p class="font-sans font-semibold md:text-[18px] text-[16px] leading-[110%] tracking-[0%] text-[#000000]">
          {{ currentQuestion.title }}
        </p>
      </div>

      <div class="ml-[20px] mt-[10px] font-open-sans font-semibold md:text-sm text-[12px] leading-none tracking-normal text-[#8A8A8A]">
        {{ currentQuestion.is_multiple_choice ? 'Выберите один или несколько вариантов ответа' : 'Выберите один вариант ответа' }}
      </div>

      <div class="ml-[20px] mt-[26px] mb-[50px] pr-[20%] flex flex-col flex-items gap-[15.88px] md:w-[673px]">
        <ProgramTestAnswer 
          v-for="(answer, index) in currentQuestion.answer_options" 
          :key="index"
          :answ="answer.text"
          :isSelected="selectedAnswers.includes(index)"
          @click="selectAnswer(index)"
        />
      </div>

      <div 
        class="flex flex-row items-center justify-center md:w-[190px] md:h-[40px] w-[144px] h-[32px] rounded-[10px] bg-[#0C1E45] md:ml-[479px] ml-[60%] mb-[20px] cursor-pointer"
        @click="nextQuestion"
      >
        <span class="md:text-[16px] text-[14px] font-semibold leading-none text-white font-sans">
          {{ isLastQuestion ? 'Завершить' : 'Далее' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { useTest } from '#imports'
import { useRouter } from 'vue-router'

const router = useRouter()

const al = ref('')
const isVisible = ref(false)

const props = defineProps({
  info: {
    type: Object,
    default: () => ({})
  }
})

const testData = ref(props.info.test)
const currentQuestionIndex = ref(0)
const selectedAnswers = ref<number[]>([])
const userAnswers = ref<{questionId: number, answerIds: number[]}[]>([])

const currentQuestion = computed(() => {
  return testData.value.questions[currentQuestionIndex.value]
})

const isLastQuestion = computed(() => {
  return currentQuestionIndex.value === testData.value.questions.length - 1
})

const selectAnswer = (index: number) => {
  if (currentQuestion.value.is_multiple_choice) {
    const answerIndex = selectedAnswers.value.indexOf(index)
    if (answerIndex === -1) {
      selectedAnswers.value.push(index)
    } else {
      selectedAnswers.value.splice(answerIndex, 1)
    }
  } else {
    selectedAnswers.value = [index]
  }
}

const nextQuestion = () => {
  // Сохраняем ответ пользователя
  userAnswers.value.push({
    questionId: currentQuestion.value.id,
    answerIds: [...selectedAnswers.value]
  })

  // Переходим к следующему вопросу или завершаем тест
  if (!isLastQuestion.value) {
    currentQuestionIndex.value++
    selectedAnswers.value = []
  } else {
    finishTest()
  }
}

const finishTest = () => {
  // Проверяем правильность ответов
  const results = userAnswers.value.map(userAnswer => {
    const question = testData.value.questions.find(q => q.id === userAnswer.questionId)
    const correctAnswers = question.answer_options
      .map((answer, index) => ({...answer, index}))
      .filter(answer => answer.is_correct)
      .map(answer => answer.index)
    
    // Для вопросов с одним правильным ответом
    if (!question.is_multiple_choice) {
      return correctAnswers[0] === userAnswer.answerIds[0]
    }
    
    // Для вопросов с несколькими правильными ответами
    const userAnswersSet = new Set(userAnswer.answerIds)
    const correctAnswersSet = new Set(correctAnswers)
    
    return (
      userAnswer.answerIds.length === correctAnswers.length &&
      userAnswer.answerIds.every(answer => correctAnswersSet.has(answer)) &&
      correctAnswers.every(answer => userAnswersSet.has(answer))
    )
  })

  const correctCount = results.filter(Boolean).length
  const score = Math.round((correctCount / testData.value.questions.length) * 100)


  const resUse = useTest()
  const savedId = localStorage.getItem('courseId');
  
  async function sendTest() {
    const result = await resUse.sendTest(props.info.test.id, score)
    console.log(result)
    try {
    const result = await resUse.sendTest(props.info.test.id, score);
    console.log('Результат теста:', result);

    if (result?.wrote?.passed) {
      if (savedId) {
        const alert = `Тест пройден. Правильных ответов: ${correctCount} из ${testData.value.questions.length} (${score}%)`
        al.value = alert
        isVisible.value = true
        setTimeout(() => {
      router.push('/study/' + savedId);
    }, 1000);
      } else {
        console.error('ID курса не найден в localStorage');
        router.push('/courses'); // Fallback
      }
    } else {

      const alert = `Тест не пройден. Правильных ответов: ${correctCount} из ${testData.value.questions.length} (${score}%)`
      al.value = alert
      isVisible.value = true
      setTimeout(() => {
      router.push('/study/' + savedId);
    }, 1000);

    }
  } catch (error) {
    console.error('Ошибка при отправке теста:', error);
  }
  }

  sendTest()
  
  console.log(`Тест завершен. Правильных ответов: ${correctCount} из ${testData.value.questions.length} (${score}%)`)

}
</script>