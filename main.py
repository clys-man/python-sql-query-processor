import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from algebra_converter import AlgebraConverter
from execution_planner import ExecutionPlanner
from graph_builder import GraphBuilder
from query_optimizer import QueryOptimizer
from sql_parser import SQLParser


class QueryProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Processador de Consultas SQL")
        self.root.geometry("1200x800")

        # Inicializar componentes
        self.parser = SQLParser()
        self.algebra_converter = AlgebraConverter()
        self.optimizer = QueryOptimizer()
        self.graph_builder = GraphBuilder()
        self.execution_planner = ExecutionPlanner()

        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Área de entrada SQL
        ttk.Label(main_frame, text="Consulta SQL:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        self.sql_input = scrolledtext.ScrolledText(main_frame, height=6, width=80)
        self.sql_input.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Botão processar
        ttk.Button(
            main_frame, text="Processar Consulta", command=self.process_query
        ).grid(row=2, column=0, pady=(0, 10))

        # Notebook para resultados
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Aba: Álgebra Relacional
        self.algebra_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.algebra_frame, text="Álgebra Relacional")

        self.algebra_text = scrolledtext.ScrolledText(
            self.algebra_frame, height=15, width=80
        )
        self.algebra_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba: Grafo de Operadores
        self.graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_frame, text="Grafo de Operadores")

        # Frame com scroll para o grafo
        canvas = tk.Canvas(self.graph_frame)
        scrollbar = ttk.Scrollbar(
            self.graph_frame, orient="vertical", command=canvas.yview
        )

        self.graph_inner_frame = ttk.Frame(canvas)
        self.graph_inner_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.graph_inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Aba: Plano de Execução
        self.execution_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.execution_frame, text="Plano de Execução")

        self.execution_text = scrolledtext.ScrolledText(
            self.execution_frame, height=15, width=80
        )
        self.execution_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def process_query(self):
        try:
            # Limpar resultados anteriores
            self.algebra_text.delete(1.0, tk.END)
            # Limpar frame do grafo
            for widget in self.graph_inner_frame.winfo_children():
                widget.destroy()
            self.execution_text.delete(1.0, tk.END)

            # Obter consulta SQL
            sql_query = self.sql_input.get(1.0, tk.END).strip()

            if not sql_query:
                messagebox.showwarning("Atenção", "Por favor, insira uma consulta SQL.")
                return

            # HU1: Parsing e Validação
            is_valid, message, parsed_query = self.parser.parse(sql_query)

            if not is_valid:
                messagebox.showerror("Erro de Validação", message)
                return

            print("parsed query", parsed_query)

            # HU2: Conversão para Álgebra Relacional
            algebra_expr = self.algebra_converter.convert(parsed_query)
            self.algebra_text.insert(1.0, "PASSO 1 - HEURÍSTICA DE JUNÇÃO:\n\n")
            self.algebra_text.insert(tk.END, algebra_expr.to_string())

            # HU4: Otimização
            optimized_algebra = self.optimizer.optimize(algebra_expr)
            self.algebra_text.insert(tk.END, "\n\n" + "=" * 60 + "\n")
            self.algebra_text.insert(
                tk.END, "PASSO 2 - HEURÍSTICA DE REDUÇÃO DE TUPLAS:\n\n"
            )
            step2 = self.optimizer._apply_tuple_reduction(algebra_expr)
            self.algebra_text.insert(tk.END, step2.to_string())
            self.algebra_text.insert(tk.END, "\n\n" + "=" * 60 + "\n")
            self.algebra_text.insert(
                tk.END, "PASSO 3 - HEURÍSTICA DE REDUÇÃO DE CAMPOS:\n\n"
            )
            self.algebra_text.insert(tk.END, optimized_algebra.to_string())

            # HU3: Construção do Grafo
            graph = self.graph_builder.build_graph(optimized_algebra)

            # Gerar grafo visual
            try:
                image_path = graph.render_graphviz(
                    filename="grafo_consulta", view=False
                )

                # Carregar e exibir imagem
                from PIL import Image, ImageTk

                img = Image.open(image_path)

                # Redimensionar se necessário
                max_width = 750
                max_height = 550
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                # Limpar frame anterior
                for widget in self.graph_inner_frame.winfo_children():
                    widget.destroy()

                # Criar label com imagem
                label = ttk.Label(self.graph_inner_frame, image=photo)
                label.image = photo  # Manter referência
                label.pack(padx=10, pady=10)

                # Adicionar botão para salvar
                save_btn = ttk.Button(
                    self.graph_inner_frame,
                    text="Salvar Grafo como PNG",
                    command=lambda: self._save_graph(image_path),
                )
                save_btn.pack(pady=5)

            except Exception as e:
                # Se falhar, mostrar mensagem de erro
                error_label = ttk.Label(
                    self.graph_inner_frame,
                    text=f"Erro ao gerar grafo visual: {
                        e
                    }\n\nVerifique se o Graphviz está instalado.",
                    foreground="red",
                )
                error_label.pack(padx=10, pady=10)

            # HU5: Plano de Execução
            execution_plan = self.execution_planner.create_plan(graph)
            self.execution_text.insert(1.0, execution_plan.to_string())

            messagebox.showinfo("Sucesso", "Consulta processada com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar consulta:\n{str(e)}")

    def _save_graph(self, image_path):
        import shutil
        from tkinter import filedialog

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Salvar Grafo",
        )

        if save_path:
            try:
                shutil.copy(image_path, save_path)
                messagebox.showinfo("Sucesso", f"Grafo salvo em:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar grafo:\n{str(e)}")


def main():
    root = tk.Tk()
    app = QueryProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
