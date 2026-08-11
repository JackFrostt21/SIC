  <template>
  <div class="flex flex-col gap-[14px] mb-[40px] last:mb-0">
    <!-- Заголовок с иконкой -->
    <div 
      @click="toggleOpen"
      class="flex items-center cursor-pointer h-[25px]"
    >
      <span class="font-sans font-semibold md:text-[18px] text-[16px] text-black">
        {{ name }}
      </span>
      <img 
        v-if="!isOpen" 
        src="../public/img/vector_up.svg" 
        class="ml-[8px] w-[15px] h-[9px]"
      />
      <img 
        v-else 
        src="../public/img/vector.svg" 
        class="ml-[8px] w-[15px] h-[9px]"
      />
    </div>

    <!-- Раскрывающийся контент -->
    <div 
      v-if="isOpen" 
      class="flex flex-col gap-[14px] transition-all duration-300"
    >
      <ProgramItem @click="readTem" v-if="longread" :type_content="'Текст'" :progress="p_longread" :img="props.info.image_course_topic"  :course_id="props.course_id" :id_topic="props.id_topic" :type_routing="'text'"/>
      <ProgramItem @click="readTem" v-if="video" :type_content="'Видео'" :progress="p_video" :img="props.info.image_course_topic"  :course_id="props.course_id" :id_topic="props.id_topic" :type_routing="'video'"/>
      <ProgramItem @click="readTem" v-if="pdf" :type_content="'PDF'" :progress="p_pdf" :img="props.info.image_course_topic"  :course_id="props.course_id" :id_topic="props.id_topic" :type_routing="'pdf'"/>
      <ProgramItem @click="readTem" v-if="audio" :type_content="'Аудио'" :progress="p_audio" :img="props.info.image_course_topic"  :course_id="props.course_id" :id_topic="props.id_topic" :type_routing="'audio'"/>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useTest } from '#imports';
import { useTems } from '#imports';

const props = defineProps({
  name: {
    default: 'Молния'
  },
  info: {
    default: {}
  },
  id_topic: {
    default: 1
  },
  course_id : {
    default: 1
  }
});

console.log('id Топика', props.id_topic)
console.log('получен id курса', props.course_id)

const isOpen = ref(false);

const longread = ref(true);
const video = ref(true);
const pdf = ref(true);
const test = ref(true);
const audio = ref(true);

const p_longread = ref(false)
const p_video = ref(false)
const p_pdf = ref(false)
const p_test = ref(false)
const p_audio = ref(false)

if (props.info.main_text === null){
  longread.value = false
}

if (props.info.pdf_file == null){
  pdf.value = false
}

if (props.info.video_file == null){
  video.value = false
}

if (props.info.training_course == null){
  test.value = false
}

if (props.info.audio_file == null){
  audio.value = false
}

if (props.info.main_text_webapp_readuser){
  p_longread.value = true
}

console.log('lon', props.info.main_text_readuser)

if (props.info.pdf_file_readuser){
  p_pdf.value = true
}

if (props.info.audio_file_readuser){
  p_audio.value = true
}

if (props.info.video_file_readuser){
  p_video.value = true
}

console.log(longread, video, pdf, test)

const toggleOpen = () => {
  isOpen.value = !isOpen.value;
};

const tem = useTems();

const readTem = async () => {

  const feedback = await tem.readTems(props.course_id, props.id_topic)
  console.log('прочитано', feedback)
}
</script>

<style>

</style>