<template>
    <div
        class="zone-editable"
        :style="{
            backgroundColor:
                form.distributions.length >= 5 && display ? '#767676' : 'white',
        }"
    >
        <div v-if="display" class="zone-display">
            <div>
                Updated: <strong>{{ updated_at }}</strong> Zone Name:
                <strong>{{ name }}</strong> Distributions:
                {{ distributionDisplay }}
            </div>

            <button
                class="btn btn-primary"
                @click="setDisplay(false)"
                :disabled="saving"
            >
                Edit
            </button>
        </div>
        <div v-else class="zone-edit">
            <label class="control-label"> Zone Name </label>

            <input
                v-model="form.name"
                placeholder="Zone name"
                class="form-control"
                :disabled="saving"
            />

            <div class="zone-edit-distributions">
                <div v-for="(distribution, i) in form.distributions" :key="i">
                    <label class="control-label"> Distribution </label>
                    <div style="display: flex">
                        <input
                            v-model="distribution.percentage"
                            placeholder="Percentage"
                            class="form-control"
                            @keypress="isNumber($event)"
                            @keyup="checkSum()"
                        />
                        <button
                            class="btn btn-error"
                            :disabled="saving"
                            @click="
                                deleteDistribution(distribution.id, form.name)
                            "
                        >
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
                <label class="control-label"> Distribution </label>
                <div style="display: flex">
                    <input
                        v-model="distributionAdd.percentage"
                        placeholder="Percentage"
                        class="form-control"
                        @keypress="isNumber($event)"
                        @keyup="checkSumAdd()"
                    />
                    <button
                        class="btn btn-success"
                        :disabled="saving || checkSumAdd() != 100"
                        @click="add"
                    >
                        +
                    </button>
                </div>
            </div>

            <div class="zone-edit-actions">
                <button
                    class="btn btn-secondary"
                    :disabled="saving"
                    @click="setDisplay(true)"
                >
                    Cancel
                </button>

                <button
                    class="btn btn-success"
                    @click="save"
                    :disabled="saving || sum !== 100"
                >
                    Save
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "ZoneEditable",
    props: {
        name: String,
        id: Number,
        distributions: Array,
        updated_at: String,
    },
    data() {
        return {
            display: true,
            form: {
                name: "",
                distributions: [],
            },
            saving: false,
            sum: 0,
            distributionAdd: { percentage: 0 },
        };
    },
    computed: {
        distributionDisplay() {
            return this.distributions
                .map((distribution) => distribution.percentage + "%")
                .join("-");
        },
    },
    mounted() {
        this.getValuesFromProps();
    },
    methods: {
        getValuesFromProps() {
            this.form.name = this.name;
            this.form.distributions = this.distributions.map((distribution) => {
                return {
                    id: distribution.id,
                    percentage: distribution.percentage,
                    idZone: distribution.zone,
                };
            });
        },
        setDisplay(value) {
            this.display = value;

            if (!this.display) {
                this.getValuesFromProps();
            }
            this.checkSum();
        },
        async save() {
            if (this.form.name !== "") {
                if (
                    this.form.name.substring(0, 1) !== " " &&
                    this.form.name.substring(
                        this.form.name.length - 1,
                        this.form.name.length
                    ) !== " "
                ) {
                    try {
                        this.saving = true;

                        const params = {
                            id: this.id,
                            name: this.form.name,
                            distributions: this.form.distributions,
                        };

                        const response = await axios.post(
                            "/api/zones/edit",
                            params
                        );
                        this.$emit("edit", {
                            name: params.name,
                            distributions: params.distributions,
                            updated_at: this.updated_at,
                        });
                        this.flashMessage.show({
                            status: "success",
                            title: "EXITO",
                            message: response.data.msg,
                        });
                    } catch (err) {
                        this.flashMessage.show({
                            status: "error",
                            title: "ERROR",
                            message: err,
                        });
                        console.log(err);
                    }
                    this.saving = false;
                    this.display = true;
                } else {
                    this.flashMessage.show({
                        status: "error",
                        title: "ERROR",
                        message:
                            "La zona no puede tener espacio al inicio o al final",
                    });
                    this.display = true;
                }
            } else {
                this.flashMessage.show({
                    status: "error",
                    title: "ERROR",
                    message: "La zona no puede estar vacia",
                });
                this.display = true;
            }
        },
        isNumber(evt) {
            evt = evt ? evt : window.event;
            var charCode = evt.which ? evt.which : evt.keyCode;
            if (
                charCode > 31 &&
                (charCode < 48 || charCode > 57) &&
                charCode !== 45
            ) {
                evt.preventDefault();
            } else {
                return true;
            }
        },
        checkSum() {
            this.sum = 0;
            this.form.distributions.forEach((element) => {
                this.sum = Number(this.sum) + Number(element.percentage);
            });
        },
        checkSumAdd() {
            let sum = 0;
            this.form.distributions.forEach((element) => {
                sum = Number(sum) + Number(element.percentage);
            });
            sum = Number(sum) + Number(this.distributionAdd.percentage);
            return sum;
        },
        async add() {
            this.saving = true;
            try {
                const params = {
                    percentage: this.distributionAdd.percentage,
                    zone: this.id,
                };
                const response = await axios.post("/api/zones/add", params);
                const data = JSON.parse(response.data.data);
                let distributions = "[";
                for (var i = 0; i < data.length; i++) {
                    if (data[i].fields.zone == this.id) {
                        distributions +=
                            '{"id":' +
                            data[i].pk +
                            ',"percentage":' +
                            data[i].fields.percentage +
                            ',"zone":"' +
                            data[i].fields.zone +
                            '"}';
                        if (i != data.length - 1) {
                            distributions += ",";
                        }
                    }
                }
                distributions += "]";
                this.$emit("add", {
                    distributions: JSON.parse(distributions),
                });
                this.flashMessage.show({
                    status: "success",
                    title: "EXITO",
                    message: response.data.msg,
                });
                this.distributionAdd.percentage = 0;
            } catch (err) {
                this.flashMessage.show({
                    status: "error",
                    title: "ERROR",
                    message: err,
                });
            }
            this.saving = false;
            this.display = true;
        },
        async deleteDistribution(idDistribution, zone) {
            try {
                this.saving = true;
                const response = await axios.get(
                    "/api/zones/delete/" + idDistribution + "/" + zone
                );
                const data = JSON.parse(response.data.data);
                let distributions = "[";
                for (var i = 0; i < data.length; i++) {
                    if (data[i].fields.zone == this.id) {
                        distributions +=
                            '{"id":' +
                            data[i].pk +
                            ',"percentage":' +
                            data[i].fields.percentage +
                            ',"zone":"' +
                            data[i].fields.zone +
                            '"}';
                        if (i != data.length - 1) {
                            distributions += ",";
                        }
                    }
                }
                if (
                    distributions.substring(
                        distributions.length - 1,
                        distributions.length
                    ) === ","
                ) {
                    distributions = distributions.substring(
                        0,
                        distributions.length - 1
                    );
                }
                distributions += "]";
                this.$emit("delete", {
                    distributions: JSON.parse(distributions),
                });
                this.flashMessage.show({
                    status: "success",
                    title: "EXITO",
                    message: response.data.msg,
                });
            } catch (err) {
                this.flashMessage.show({
                    status: "error",
                    title: "ERROR",
                    message: err,
                });
            }
            this.saving = false;
            this.display = true;
        },
    },
};
</script>

<style lang="scss">
@import "resources/scss/variables.scss";

.zone-editable {
    border: 1px solid $gray-color;
    padding: $qmb;
    border-radius: $border-radius;

    .zone-display {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .zone-edit {
        display: flex;
        flex-direction: column;
        gap: $small-action-space;

        .zone-edit-actions {
            display: flex;
            gap: $small-action-space;
            justify-content: end;
        }

        .zone-edit-distributions {
            display: grid;
            grid-template-columns: repeat(1, 1fr);
            gap: $small-action-space;
        }
    }
}
</style>
