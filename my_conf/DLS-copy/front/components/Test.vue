<!-- Modal.vue -->
<template>
  <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-[1000]">
    <div class="w-[491px] h-[402px] rounded-[10px] bg-white relative">

      <p class="absolute top-[20px] left-[20px] w-[199px] h-[30px] font-[600] text-[22px] leading-[1] tracking-[0] font-sans text-black">
        Изменить пароль
      </p>

      <div className="absolute top-[74px] left-[20px] w-[460px] h-[83px]">

        <span class="w-[49px] h-[22px] font-open-sans font-normal text-[16px] leading-[1] tracking-normal text-[#8A8A8A]">
          Логин
        </span>

        <input
          id="inputLogin"
          type="text"
          v-model="login"
          class="w-[451px] h-[46px] mt-[6px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] 
          text-black bg-[#E6E6E6] focus:outline-none focus:ring-1 focus:ring-[#909090] not-placeholder-shown:bg-white"
        />

      </div>

      <div class="absolute left-5 top-[164px] w-[451px] h-[136px]">

        <span class="w-[115px] h-[22px] font-open-sans font-normal text-[16px] leading-[1] tracking-normal text-[#8A8A8A]">
          Новый пароль
        </span> 
        
        <input
          id="inputPassword"
          type="text"
          v-model="password"
          class="w-[451px] h-[46px] mt-[6px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] 
          text-black bg-[#E6E6E6] focus:outline-none focus:ring-1 focus:ring-[#909090] not-placeholder-shown:bg-white"
        />

        <div class="absolute top-[82px] w-[451px] h-[54px] text-[#8A8A8A] font-normal text-base leading-[1.1] left-0 font-open-sans">
          Пароль должен соответствовать формату. Используйте 8 и более символов: латинские буквы (a-z) и минимум одну цифру.
        </div>

      </div>

      <div @click="close" class="absolute top-[332px] left-[20px] w-[190px] h-[40px] flex flex-row items-center rounded-[10px] pt-[17px] pb-[17px] pl-[80px] pr-[80px] gap-[10px]">

        <a class="w-[82px] h-[22px] font-semibold text-base leading-[100%] underline underline-offset-0 decoration-solid text-[#0C1E45] font-open-sans flex items-center justify-center">
          Отменить
        </a>

      </div>

      <div @click="change" class="flex flex-row w-[190px] h-[40px] rounded-[10px] items-center  bg-[#0C1E45] top-[332px] left-[281px] absolute">

        <span
  class="w-[88px] h-[22px] font-open-sans font-semibold text-[16px] ml-[51px] leading-[1] tracking-normal text-white"
>
  Сохранить
</span>

      </div>



    </div>
  </div>
</template>

<script setup>
import { useChangePassword } from '#imports';

const changePassword = useChangePassword();
const password = ref('');

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};

const change = async () => {
  const feedback = await changePassword.change({
    password: password.value,
  });
  emit('close');
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 5px;
  max-width: 500px;
  min-width: 300px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.modal-header,
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
}

.modal-body {
  padding: 10px;
}

.btn-close {
  border: none;
  font-size: 20px;
  cursor: pointer;
  background: transparent;
}

.btn-secondary {
  padding: 8px 16px;
  background-color: #ccc;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>