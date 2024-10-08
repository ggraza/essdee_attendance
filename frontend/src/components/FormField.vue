<template>
	<div v-if="showField" class="flex flex-col gap-1.5">
		<!-- Label -->
		<span
			v-if="
				!['Check', 'Section Break', 'Column Break'].includes(props.fieldtype)
			"
			:class="[
				// mark field as mandatory
				props.reqd ? `after:content-['_*'] after:text-red-600` : ``,
				`block text-sm leading-5 text-gray-700`,
			]"
		>
			{{ props.label }}
		</span>

		<!-- Select or Link field with predefined options -->
		<Autocomplete
			v-if="props.fieldtype === 'Select' || props.documentList"
			:class="isReadOnly ? 'pointer-events-none' : ''"
			:placeholder="`Select ${props.label}`"
			:options="selectionList"
			:modelValue="modelValue"
			v-bind="$attrs"
			:disabled="isReadOnly"
			@update:modelValue="(v) => emit('update:modelValue', v?.value)"
		/>

		<!-- Link field -->
		<Link
			v-else-if="props.fieldtype === 'Link'"
			:doctype="props.options"
			:modelValue="modelValue"
			:filters="props.linkFilters"
			:disabled="isReadOnly"
			@update:modelValue="(v) => emit('update:modelValue', v)"
		/>

		<!-- Text -->
		<Input
			v-else-if="
				['Text Editor', 'Small Text', 'Text', 'Long Text'].includes(
					props.fieldtype
				)
			"
			type="textarea"
			:value="modelValue"
			:placeholder="`Enter ${props.label}`"
			@input="(v) => emit('update:modelValue', v)"
			@change="(v) => emit('change', v)"
			v-bind="$attrs"
			:disabled="isReadOnly"
			class="h-15"
		/>

		<!-- Check -->
		<Input
			v-else-if="props.fieldtype === 'Check'"
			type="checkbox"
			:label="props.label"
			:value="modelValue"
			@input="(v) => emit('update:modelValue', v)"
			@change="(v) => emit('change', v)"
			v-bind="$attrs"
			:disabled="isReadOnly"
			class="rounded-sm text-gray-800"
		/>

		<!-- Data field -->
		<Input
			v-else-if="props.fieldtype === 'Data'"
			type="text"
			:value="modelValue"
			@input="(v) => emit('update:modelValue', v)"
			@change="(v) => emit('change', v)"
			v-bind="$attrs"
			:disabled="isReadOnly"
		/>

		<!-- Read only currency field -->
		<Input
			v-else-if="props.fieldtype === 'Currency' && isReadOnly"
			type="text"
			:value="modelValue"
			@input="(v) => emit('update:modelValue', v)"
			@change="(v) => emit('change', v)"
			v-bind="$attrs"
			:disabled="isReadOnly"
		/>

		<!-- Float/Int field -->
		<Input
			v-else-if="isNumberType"
			type="number"
			:value="modelValue"
			@input="(v) => emit('update:modelValue', v)"
			@change="(v) => emit('change', v)"
			v-bind="$attrs"
			:disabled="isReadOnly"
		/>

		<!-- Section Break -->
		<div
			v-else-if="props.fieldtype === 'Section Break'"
			:class="props.addSectionPadding ? 'mt-2' : ''"
		>
			<h2
				v-if="props.label"
				class="text-base font-semibold text-gray-800"
				:class="props.addSectionPadding ? 'pt-4' : ''"
			>
				{{ props.label }}
			</h2>
		</div>

		<!-- Date -->
		<!-- FIXME: default datepicker has poor UI -->
		<Input
			v-else-if="props.fieldtype === 'Date'"
			type="date"
			v-model="date"
			:value="modelValue"
			:placeholder="`Select ${props.label}`"
			:formatValue="(val) => dayjs(val).format('DD-MM-YYYY')"
			@input="(v) => emit('update:modelValue', v)"
			@change="(v) => emit('change', v)"
			v-bind="$attrs"
			:disabled="isReadOnly"
			:min="props.minDate"
			:max="props.maxDate"
		/>

		<input class="border-gray-400 placeholder-gray-500 form-input block w-full"
			v-else-if="props.fieldtype === 'Time'"
			type="time"
			:value='modelValue'
			:placeholder="`Select ${props.label}`"
			@input="(v) => emit('update:modelValue', v.target.value)"
			@change="(v) => emit('change', v.target.value)"
			v-bind="$attrs"
			:disabled="isReadOnly"
		>
		<!-- Datetime -->

		<ErrorMessage :message="props.errorMessage" />
	</div>
</template>

<script setup>
import { Autocomplete, ErrorMessage } from "frappe-ui"
import { ref, computed, onMounted, inject } from "vue"
import Link from "@/components/Link.vue"

const props = defineProps({
	field:String,
	fieldtype: String,
	fieldname: String,
	modelValue: [String, Number, Boolean, Array, Object],
	default: [String, Number, Boolean, Array, Object],
	label: String,
	options: [String, Array],
	linkFilters: Object,
	documentList: Array,
	readOnly: [Boolean, Number],
	reqd: [Boolean, Number],
	hidden: {
		type: [Boolean, Number],
		default: false,
	},
	errorMessage: String,
	minDate: String,
	maxDate: String,
	addSectionPadding: {
		type: Boolean,
		default: true,
	},
})

const emit = defineEmits(["change", "update:modelValue"])
const dayjs = inject("$dayjs")

let date = ref(null)

const showField = computed(() => {
	if (props.readOnly && !isLayoutField.value && !props.modelValue) return false

	return props.fieldtype !== "Table" && !props.hidden
})

const isNumberType = computed(() => {
	return ["Int", "Float", "Currency"].includes(props.fieldtype)
})

const isLayoutField = computed(() => {
	return ["Section Break", "Column Break"].includes(props.fieldtype)
})

const isReadOnly = computed(() => {
	return Boolean(props.readOnly)
})

const selectionList = computed(() => {
	if (props.fieldtype === "Link" && props.documentList) {
		return props.documentList
	} else if (props.fieldtype == "Select" && props.options) {
		const options = props.options.split("\n")
		return options.map((option) => ({
			label: option,
			value: option,
		}))
	}

	return []
})

function setDefaultValue() {
	if (props.modelValue) return

	if (props.default) {
		if (props.fieldtype === "Check") {
			emit("update:modelValue", props.default === "1" ? true : false)
		} else if (props.fieldtype === "Date" && props.default === "Today") {
			emit("update:modelValue", dayjs().format("YYYY-MM-DD"))
		} else if (isNumberType.value) {
			emit("update:modelValue", parseFloat(props.default || 0))
		} else {
			emit("update:modelValue", props.default)
		}
	} else {
		props.fieldtype === "Check"
			? emit("update:modelValue", false)
			: emit("update:modelValue", "")
	}
}

onMounted(() => {
	setDefaultValue()
})
</script>
