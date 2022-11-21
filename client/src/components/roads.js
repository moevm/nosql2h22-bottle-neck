import * as React from 'react';
import InputComponent from "./inputComponent";
import Dropdown from 'react-dropdown';
import 'react-dropdown/style.css';

export default function Roads() {
    const options = [
        'Тип дорог','Перекресток', 'Проспект', 'Улица'
    ];
    const defaultOption = options[0];
    return (<div>
        <InputComponent label={"Адрес/имя"} type={"text"} value={"Введите что-то"}/>
        <Dropdown options={options}  value={defaultOption} placeholder="Select an option" />
        <div class="inline">
            <div>
            Диапазон загруженности
                <div class="inline">
                    <InputComponent label={"Min"} type={"Number"}
                        onChange={() => console.log(1)}/>
                    <InputComponent label={"Max"} type={"Number"}
                        onChange={() => console.log(1)}/>
                </div>
            </div>
            <button>Отфильтровать</button>
        </div>
        <p></p>
        <div >
            {getTable()}
        </div>
    </div>)
    function getTable(){
        let table = []
        table.push(<tr>
            <th>Адрес/имя</th>
            <th>Тип дороги</th>
            <th>Загруженнсоть</th>
        </tr>);
        return <table>{table}</table>
    }
}