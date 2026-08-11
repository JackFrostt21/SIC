<template>

  <div class="md:w-[1040px] w-full h-[135px] rounded-[10px] bg-white flex flex-row gap-[40px] items-center">

    <div class="w-fit h-[90%] flex items-center ml-[20px]">
      <img v-if="props.type_routing === 'test'"
        :src="props.img || '/img/test.svg'" 
        class="max-w-full max-h-full object-contain rounded-[10px]"
      >
      <img v-if="props.type_routing === 'text'"
        :src="props.img || '/img/longread.svg'" 
        class="max-w-full max-h-full object-contain rounded-[10px]"
      >
      <img v-if="props.type_routing === 'pdf'"
        :src="props.img || '/img/pdf.svg'" 
        class="max-w-full max-h-full object-contain rounded-[10px]"
      >
      <img v-if="props.type_routing === 'video'"
        :src="props.img || '/img/video.svg'" 
        class="max-w-full max-h-full object-contain rounded-[10px]"
      >
      <img v-if="props.type_routing === 'audio'"
        :src="props.img || '/img/video.svg'" 
        class="max-w-full max-h-full object-contain rounded-[10px]"
      >
    </div>

    <div class="flex flex-col md:gap-[15px] gap-[6px]">

    <div class="md:w-[555.02px]">
      <p class="font-sans font-semibold md:text-[14px] text-[12px] leading-[100%] tracking-[0%] text-[#8A8A8A]">{{ type_content }}</p>
    </div>

    <div class="md:w-[555.02px] max-w-[70%]">
      <p class="font-open-sans font-semibold md:text-[16px] text-[14px] leading-[100%] tracking-[0%] text-[#000000]">{{ type_content }}</p>
    </div>

    <div class="flex flex-row gap-[10px] items-center">

    <NuxtLink v-if="props.type_routing === 'video'" :to="'/study/video/' + props.id_topic + '/'">
    <ProgramButtonGo class="" />
    </NuxtLink>

    <NuxtLink v-if="props.type_routing === 'text'" :to="'/study/longread/' + props.id_topic + '/'">
    <ProgramButtonGo class="" :isComplete="progress"/>
    </NuxtLink>

    <NuxtLink v-if="props.type_routing === 'test'" :to="'/study/test/' + props.course_id + '/'">
    <ProgramButtonGo class="" />
    </NuxtLink>

    <NuxtLink v-if="props.type_routing === 'pdf'" :to="'/study/pdf/' + props.id_topic +'/'">
    <ProgramButtonGo class="" />
    </NuxtLink>

    <NuxtLink v-if="props.type_routing === 'audio'" :to="'/study/audio/' + props.id_topic + '/'">
    <ProgramButtonGo class="" />
    </NuxtLink>

    <div v-if="props.obligator" class="md:w-[138px] md:h-[22px] w-[102px] h-[16px] relative items-center">

      <img src="../public/img/alert-circle.svg" class="absolute md:top-[2px] top-[1px]"/>

      <span class="md:block hidden md:w-[115px] w-[85px] h-[22px] inline-flex items-center font-bold md:text-[16px] text-[14px] leading-[1] text-[#D21E41] font-sans absolute left-[23px] top-[1px] md:top-[5px]">
        Обязательно!
      </span>

    </div>

    </div>

    </div>
  </div>
</template>



<script setup>

const props = defineProps({
  type_content: {
    type: String, // Укажите правильный тип, если знаете
    default: 'Тест'
  },
  obligator: {
    type: Boolean, // Лучше указать тип
    default: false
  },
  progress: {
    type: Boolean, // Лучше указать тип
  },
  img: {
    default: '../public/img/courceimg.svg'
  },
  id_topic: {
    default: 1
  },
  course_id: {
    default: 1
  },
  type_routing: {
    default: ''
  }
})

console.log(props.progress);

const topicStore = useCoursesStore();

const topic = topicStore.topics.find(topic => topic.id === Number(props.id_topic));

console.log('Наш топик', topic)

const pdf = topic.pdf_file
const video = topic.video_file
const audio = topic.audio_file
const title = topic.title
console.log(props.type_content, props.progress)
</script>



<style>

</style>