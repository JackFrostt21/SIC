<template>
  <div class="flex flex-col w-[90%] md:w-[1040px] md:h-[169px] h-[125px] relative mx-auto rounded-[10px] px-[16px] gap-[10px] bg-white">

    <img :src="url" class="absolute w-[64px] h-[64px] md:w-[129px] md:h-[128px] left-[16px] top-[20px] rounded-[316px] object-cover" />

    <div class="absolute flex flex-col md:w-[567px] md:h-[67px] h-[43px] top-[25px] md:left-[160px] left-[93px] md:gap-[5px] gap-[3px]">

      <span class="md:w-[567px] h-[25px] font-semibold md:text-[18px] text-[14px] leading-[1] tracking-normal text-black font-sans">
        {{ full_name }}
      </span>

      <span class="font-medium md:text-[14px] text-[12px] leading-[1.15] text-[#8A8A8A]" style="font-family: 'Inter', sans-serif;">
        {{ email }}
      </span>

      <span class="font-medium md:text-[14px] text-[12px] leading-[1.15] text-[#8A8A8A]" style="font-family: 'Inter', sans-serif;">
        {{phone}}
      </span>

    </div>

    <!--div class="absolute top-[115px] left-[156px] flex items-center border border-[#00DCC8] rounded-[20px] h-[27.26px] w-fit border-2 px-4 py-1 gap-[10px]">
      <img src="/img/i-award.svg" class="h-[20px]" />
      <p class="text-[14.51px] font-semibold font-sans leading-none">2 место</p>
    </div>

    <div class="absolute left-[278px] top-[115px] flex items-center w-[92.21px] h-[27.26px] px-[13.6px] py-[3.63px] gap-[9.07px] rounded-[19.95px] border border-[#00DCC8] border-[1.81px]">
      <p class="text-[14.51px] font-semibold font-sans leading-none">5 баллов</p>
    </div-->

  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useUserStore } from '#imports';

const store = useUserStore()
const url = store.image;

export default {
  computed: {
    username() {
      return useAuthStore().user?.username;
    },
    email() {
      return useUserStore().email;
    },
    full_name() {
      return useUserStore().full_name;
    },
    phone() {
      return useUserStore().phone;
    },
    url() {
      return useUserStore().image
    }
  },
  async mounted() {
    const getUser  = useUser();
    const result = await getUser.getUser();

    console.log(result);
    
    if (!result.success) {
      // Обработать ошибку
    }
  }
}
</script>


<style>

</style>