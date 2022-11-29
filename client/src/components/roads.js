import * as React from 'react';
import InputComponent from "./inputComponent";

import 'react-dropdown/style.css';

export default function Roads({typeRoads, address, minWorkload, maxWorkload, filter, data}) {
    const getInitialState = () => {
        const value = "Тип дорог";
        return value;
    };
    const [value, setValue] = React.useState(getInitialState);

    const handleChange = (e) => {
        setValue(e.target.value);
    };
    return (<div>
        <InputComponent label={"Адрес/имя"} type={"text"} value={"Введите что-то"} sRef={address}/>
        <select value={value} ref={typeRoads} onChange={handleChange}>
            <option value="Тип дорог">Тип дорог</option>
            <option value="Перекресток">Перекресток</option>
            <option value="Улица">Улица</option>
            <option value="Проспект">Проспект</option>
        </select>
        <div class="inline">
            <div>
            Диапазон загруженности
                <div class="inline">
                    <InputComponent label={"Min"} type={"Number"}
                        onChange={() => console.log(1)} sRef={minWorkload}/>
                    <InputComponent label={"Max"} type={"Number"}
                        onChange={() => console.log(1)} sRef={maxWorkload}/>
                </div>
            </div>
            <button onClick={filter}>Отфильтровать</button>
        </div>
        <p></p>
        <div >
            {getTable()}
        </div>
    </div>)
    function getTable(){
        let table = []
        table.push(
            <table>
                <thead>
                <tr>
                    <th>Адрес/имя</th>
                    <th>Тип дороги</th>
                    <th>Загруженнсоть</th>
                </tr>
                </thead>
            </table>
        );
        if(data != null){
            let content = []
            for(let i = 0; i < data.length; i++){
                content.push(<tr>
                    <td>{data[i].address}</td>
                    <td>{Number(1+Math.random()*10)}</td>
                    <td>{data[i].workload}</td>
                </tr>)
            }
            table.push(<div className="table-scroll-body"><table><tbody>{content}</tbody></table></div>)
        }
        return <div className="table-scroll">{table}</div>
    }
}