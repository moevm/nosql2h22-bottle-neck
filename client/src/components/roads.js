import * as React from 'react';
import InputComponent from "./inputComponent";

import 'react-dropdown/style.css';

export default function Roads({typeRoads, address, minWorkload, maxWorkload, filter, data, dataMaxLen}) {
    const getInitialState = () => {
        const value = "Тип дорог";
        return value;
    };
    const [value, setValue] = React.useState(getInitialState);

    const handleChange = (e) => {
        setValue(e.target.value);
    };
    return (<div>
        <InputComponent label={"Адрес/имя"} type={"text"} placeholder={"Введите что-то"} sRef={address}/>
        <select value={value} ref={typeRoads} onChange={handleChange}>
            <option value="">Тип дорог</option>
            <option value="motorway">motorway</option>
            <option value="trunk">trunk</option>
            <option value="primary">primary</option>
            <option value="secondary">secondary</option>
            <option value="residential">residential</option>
            <option value="tertiary">tertiary</option>
            <option value="secondary_link">secondary link</option>
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
        if(data != null)
            table.push(<div>Количество дорог {data.length}/{dataMaxLen}</div>)
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
                    <td>{data[i].type}</td>
                    <td>{data[i].workload}</td>
                </tr>)
            }
            table.push(<div className="table-scroll-body"><table><tbody>{content}</tbody></table></div>)
        }
        return <div className="table-scroll">{table}</div>
    }
}